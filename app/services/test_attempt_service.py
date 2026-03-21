from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from app.core.logging_config import get_logger
from app.core.timezone_utils import convert_to_msk_naive
from app.database.crud.test_crud import get_test_by_token, increment_attempts_count
from app.database.crud.test_attempt_crud import create_attempt, get_attempt_by_id, submit_attempt
from app.database.crud.test_attempt_profile_value_crud import create_profile_value, get_profile_values_by_attempt
from app.database.crud.test_profile_field_crud import get_profile_fields_by_test
from app.database.crud.question_crud import get_questions_by_test, count_questions_by_test, get_question_by_id
from app.database.crud.question_option_crud import get_option_by_id
from app.database.crud.user_answer_crud import create_user_answer, get_answers_by_attempt, get_answer_by_question
from app.database.crud.user_answer_option_crud import create_answer_option
from app.database.models.enums import QuestionType, ProfileFieldType
from app.schemas.test_attempt import (
    AttemptCreate,
    AnswersSubmit,
    AttemptResponse,
    ProgressResponse,
    SubmitResponse
)

logger = get_logger(__name__)


class AttemptError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


async def create_attempt_service(
    session: AsyncSession,
    token: str,
    attempt_data: AttemptCreate
) -> AttemptResponse:
    logger.info(
        "Starting attempt creation",
        operation="create_attempt_service",
        token=token,
        client_name=attempt_data.client_name
    )
    
    try:
        test = await get_test_by_token(session, token)
        
        if not test:
            logger.warning(
                "Test not found by token",
                operation="create_attempt_service",
                token=token
            )
            raise AttemptError("token", f"Тест с токеном {token} не найден")
        
        if test.access_until and test.access_until < datetime.utcnow():
            logger.warning(
                "Test access expired",
                operation="create_attempt_service",
                test_id=test.id,
                access_until=test.access_until
            )
            raise AttemptError("token", "Срок доступа к тесту истек")
        
        profile_fields = await get_profile_fields_by_test(session, test.id)
        required_field_ids = {pf.id for pf in profile_fields if pf.is_required}
        provided_field_ids = {pv.profile_field_id for pv in attempt_data.profile_values}
        
        logger.info(
            "Validating profile fields",
            operation="create_attempt_service",
            test_id=test.id,
            required_field_ids=list(required_field_ids),
            provided_field_ids=list(provided_field_ids),
            all_profile_fields=[{"id": pf.id, "label": pf.label, "is_required": pf.is_required} for pf in profile_fields]
        )
        
        missing_fields = required_field_ids - provided_field_ids
        if missing_fields:
            missing_field_names = [pf.label for pf in profile_fields if pf.id in missing_fields]
            logger.warning(
                "Missing required profile fields",
                operation="create_attempt_service",
                missing_field_ids=list(missing_fields),
                required_fields=[{"id": pf.id, "label": pf.label} for pf in profile_fields if pf.id in missing_fields]
            )
            raise AttemptError(
                "profile_values", 
                f"Не заполнены обязательные поля профиля: {', '.join(missing_field_names)} (ID: {missing_fields})"
            )
        
        attempt = await create_attempt(session, test.id, attempt_data.client_name)
        
        for pv_data in attempt_data.profile_values:
            await create_profile_value(
                session,
                attempt.id,
                pv_data.profile_field_id,
                text_value=pv_data.text_value,
                number_value=pv_data.number_value,
                date_value=pv_data.date_value
            )
        
        await increment_attempts_count(session, test.id)
        
        total_questions = await count_questions_by_test(session, test.id)
        
        await session.commit()
        
        logger.info(
            "Attempt created successfully",
            operation="create_attempt_service",
            attempt_id=attempt.id,
            test_id=test.id
        )
        
        return AttemptResponse(
            attempt_id=attempt.id,
            test_id=test.id,
            test_title=test.title,
            client_name=attempt.client_name,
            started_at=attempt.started_at,
            total_questions=total_questions
        )
        
    except AttemptError:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(
            "Unexpected error during attempt creation",
            operation="create_attempt_service",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def save_answers_service(
    session: AsyncSession,
    attempt_id: int,
    answers_data: AnswersSubmit
) -> dict:
    logger.info(
        "Starting answers save",
        operation="save_answers_service",
        attempt_id=attempt_id,
        answers_count=len(answers_data.answers)
    )
    
    try:
        attempt = await get_attempt_by_id(session, attempt_id)
        
        if not attempt:
            logger.warning(
                "Attempt not found",
                operation="save_answers_service",
                attempt_id=attempt_id
            )
            raise AttemptError("attempt_id", f"Попытка с ID {attempt_id} не найдена")
        
        if attempt.submitted_at:
            logger.warning(
                "Attempt already submitted",
                operation="save_answers_service",
                attempt_id=attempt_id,
                submitted_at=attempt.submitted_at
            )
            raise AttemptError("attempt_id", "Тест уже завершен, нельзя изменить ответы")
        
        saved_count = 0
        updated_count = 0
        
        for answer_data in answers_data.answers:
            question = await get_question_by_id(session, answer_data.question_id)
            
            if not question:
                logger.warning(
                    "Question not found",
                    operation="save_answers_service",
                    question_id=answer_data.question_id
                )
                raise AttemptError("question_id", f"Вопрос с ID {answer_data.question_id} не найден")
            
            if question.test_id != attempt.test_id:
                logger.warning(
                    "Question does not belong to test",
                    operation="save_answers_service",
                    question_id=answer_data.question_id,
                    question_test_id=question.test_id,
                    attempt_test_id=attempt.test_id
                )
                raise AttemptError("question_id", f"Вопрос {answer_data.question_id} не принадлежит этому тесту")
            
            existing_answer = await get_answer_by_question(session, attempt_id, answer_data.question_id)
            
            datetime_value = None
            if answer_data.datetime_answer is not None:
                datetime_value = convert_to_msk_naive(answer_data.datetime_answer)
            
            if existing_answer:
                if answer_data.text_answer is not None:
                    existing_answer.text_answer = answer_data.text_answer
                if answer_data.boolean_answer is not None:
                    existing_answer.boolean_answer = answer_data.boolean_answer
                if answer_data.number_answer is not None:
                    existing_answer.number_answer = answer_data.number_answer
                if datetime_value is not None:
                    existing_answer.datetime_answer = datetime_value
                
                await session.flush()
                user_answer = existing_answer
                updated_count += 1
            else:
                user_answer = await create_user_answer(
                    session,
                    attempt_id,
                    answer_data.question_id,
                    text_answer=answer_data.text_answer,
                    boolean_answer=answer_data.boolean_answer,
                    number_answer=answer_data.number_answer,
                    datetime_answer=datetime_value
                )
                saved_count += 1
            
            if answer_data.selected_option_ids:
                for option_id in answer_data.selected_option_ids:
                    option = await get_option_by_id(session, option_id)
                    if not option or option.question_id != answer_data.question_id:
                        logger.warning(
                            "Invalid option for question",
                            operation="save_answers_service",
                            option_id=option_id,
                            question_id=answer_data.question_id
                        )
                        raise AttemptError("selected_option_ids", f"Опция {option_id} не принадлежит вопросу {answer_data.question_id}")
                    
                    await create_answer_option(session, user_answer.id, option_id)
        
        await session.commit()
        
        logger.info(
            "Answers saved successfully",
            operation="save_answers_service",
            attempt_id=attempt_id,
            saved_count=saved_count,
            updated_count=updated_count
        )
        
        return {
            "saved": saved_count,
            "updated": updated_count,
            "total": saved_count + updated_count
        }
        
    except AttemptError:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(
            "Unexpected error during answers save",
            operation="save_answers_service",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def get_progress_service(
    session: AsyncSession,
    attempt_id: int
) -> ProgressResponse:
    logger.info(
        "Getting attempt progress",
        operation="get_progress_service",
        attempt_id=attempt_id
    )
    
    try:
        attempt = await get_attempt_by_id(session, attempt_id)
        
        if not attempt:
            logger.warning(
                "Attempt not found",
                operation="get_progress_service",
                attempt_id=attempt_id
            )
            raise AttemptError("attempt_id", f"Попытка с ID {attempt_id} не найдена")
        
        total_questions = await count_questions_by_test(session, attempt.test_id)
        user_answers = await get_answers_by_attempt(session, attempt_id)
        answered_question_ids = {answer.question_id for answer in user_answers}
        
        all_questions = await get_questions_by_test(session, attempt.test_id)
        all_question_ids = {q.id for q in all_questions}
        
        unanswered_ids = list(all_question_ids - answered_question_ids)
        answered_count = len(answered_question_ids)
        
        progress_percent = (answered_count / total_questions * 100) if total_questions > 0 else 0
        
        logger.info(
            "Progress calculated",
            operation="get_progress_service",
            attempt_id=attempt_id,
            progress=progress_percent
        )
        
        return ProgressResponse(
            attempt_id=attempt_id,
            total_questions=total_questions,
            answered_questions=answered_count,
            progress_percent=round(progress_percent, 2),
            unanswered_question_ids=unanswered_ids
        )
        
    except AttemptError:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during progress calculation",
            operation="get_progress_service",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def submit_attempt_service(
    session: AsyncSession,
    attempt_id: int
) -> SubmitResponse:
    logger.info(
        "Starting attempt submission",
        operation="submit_attempt_service",
        attempt_id=attempt_id
    )
    
    try:
        attempt = await get_attempt_by_id(session, attempt_id)
        
        if not attempt:
            logger.warning(
                "Attempt not found",
                operation="submit_attempt_service",
                attempt_id=attempt_id
            )
            raise AttemptError("attempt_id", f"Попытка с ID {attempt_id} не найдена")
        
        if attempt.submitted_at:
            logger.warning(
                "Attempt already submitted",
                operation="submit_attempt_service",
                attempt_id=attempt_id,
                submitted_at=attempt.submitted_at
            )
            raise AttemptError("attempt_id", "Тест уже был завершен ранее")
        
        all_questions = await get_questions_by_test(session, attempt.test_id)
        required_question_ids = {q.id for q in all_questions}
        
        user_answers = await get_answers_by_attempt(session, attempt_id)
        answered_question_ids = {answer.question_id for answer in user_answers}
        
        missing_questions = required_question_ids - answered_question_ids
        if missing_questions:
            logger.warning(
                "Missing required answers",
                operation="submit_attempt_service",
                attempt_id=attempt_id,
                missing_question_ids=list(missing_questions)
            )
            raise AttemptError("answers", f"Не отвечены обязательные вопросы: {missing_questions}")
        
        submitted_attempt = await submit_attempt(session, attempt_id)
        
        await session.commit()
        
        logger.info(
            "Attempt submitted successfully",
            operation="submit_attempt_service",
            attempt_id=attempt_id,
            submitted_at=submitted_attempt.submitted_at
        )
        
        return SubmitResponse(
            attempt_id=attempt_id,
            submitted_at=submitted_attempt.submitted_at,
            can_view_report=attempt.test.client_can_view_report,
            message="Тест успешно завершен" + (" Отчет доступен для просмотра" if attempt.test.client_can_view_report else "")
        )
        
    except AttemptError:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(
            "Unexpected error during attempt submission",
            operation="submit_attempt_service",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
