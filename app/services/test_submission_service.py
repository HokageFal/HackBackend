from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List

from app.core.logging_config import get_logger
from app.core.timezone_utils import convert_to_msk_naive
from app.database.crud.test_crud import get_test_by_token, increment_attempts_count
from app.database.crud.test_attempt_crud import create_attempt, submit_attempt
from app.database.crud.test_attempt_profile_value_crud import create_profile_value
from app.database.crud.test_profile_field_crud import get_profile_fields_by_test
from app.database.crud.question_crud import get_question_by_id
from app.database.crud.question_option_crud import get_option_by_id
from app.database.crud.user_answer_crud import create_user_answer
from app.database.crud.user_answer_option_crud import create_answer_option
from app.schemas.test_submission import TestSubmission, SubmissionResponse

logger = get_logger(__name__)


class SubmissionError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


async def submit_test_service(
    session: AsyncSession,
    token: str,
    submission: TestSubmission
) -> SubmissionResponse:
    logger.info(
        "Starting test submission",
        operation="submit_test_service",
        token=token,
        client_name=submission.client_name,
        answers_count=len(submission.answers)
    )
    
    try:
        test = await get_test_by_token(session, token)
        
        if not test:
            logger.warning(
                "Test not found by token",
                operation="submit_test_service",
                token=token
            )
            raise SubmissionError("token", f"Тест с токеном {token} не найден")
        
        if test.access_until and test.access_until < datetime.utcnow():
            logger.warning(
                "Test access expired",
                operation="submit_test_service",
                test_id=test.id,
                access_until=test.access_until
            )
            raise SubmissionError("token", "Срок доступа к тесту истек")
        
        profile_fields = await get_profile_fields_by_test(session, test.id)
        required_field_ids = {pf.id for pf in profile_fields if pf.is_required}
        provided_field_ids = {pv.profile_field_id for pv in submission.profile_values}
        
        missing_fields = required_field_ids - provided_field_ids
        if missing_fields:
            missing_field_names = [pf.label for pf in profile_fields if pf.id in missing_fields]
            logger.warning(
                "Missing required profile fields",
                operation="submit_test_service",
                missing_field_ids=list(missing_fields)
            )
            raise SubmissionError(
                "profile_values",
                f"Не заполнены обязательные поля профиля: {', '.join(missing_field_names)}"
            )
        
        attempt = await create_attempt(session, test.id, submission.client_name)
        
        logger.info(
            "Attempt created",
            operation="submit_test_service",
            attempt_id=attempt.id
        )
        
        for pv_data in submission.profile_values:
            datetime_value = None
            if pv_data.datetime_value:
                datetime_value = convert_to_msk_naive(pv_data.datetime_value)
            
            await create_profile_value(
                session,
                attempt.id,
                pv_data.profile_field_id,
                text_value=pv_data.text_value,
                number_value=pv_data.number_value,
                date_value=pv_data.date_value,
                datetime_value=datetime_value
            )
        
        logger.info(
            "Profile values saved",
            operation="submit_test_service",
            count=len(submission.profile_values)
        )
        
        for answer_data in submission.answers:
            question = await get_question_by_id(session, answer_data.question_id)
            
            if not question:
                logger.warning(
                    "Question not found",
                    operation="submit_test_service",
                    question_id=answer_data.question_id
                )
                raise SubmissionError("question_id", f"Вопрос с ID {answer_data.question_id} не найден")
            
            if question.test_id != test.id:
                logger.warning(
                    "Question does not belong to test",
                    operation="submit_test_service",
                    question_id=answer_data.question_id,
                    question_test_id=question.test_id,
                    test_id=test.id
                )
                raise SubmissionError("question_id", f"Вопрос {answer_data.question_id} не принадлежит этому тесту")
            
            datetime_value = None
            if answer_data.datetime_answer:
                datetime_value = convert_to_msk_naive(answer_data.datetime_answer)
            
            user_answer = await create_user_answer(
                session,
                attempt.id,
                answer_data.question_id,
                text_answer=answer_data.text_answer,
                boolean_answer=answer_data.boolean_answer,
                number_answer=answer_data.number_answer,
                datetime_answer=datetime_value
            )
            
            if answer_data.selected_option_ids:
                for option_id in answer_data.selected_option_ids:
                    option = await get_option_by_id(session, option_id)
                    if not option or option.question_id != answer_data.question_id:
                        logger.warning(
                            "Invalid option for question",
                            operation="submit_test_service",
                            option_id=option_id,
                            question_id=answer_data.question_id
                        )
                        raise SubmissionError(
                            "selected_option_ids",
                            f"Опция {option_id} не принадлежит вопросу {answer_data.question_id}"
                        )
                    
                    await create_answer_option(session, user_answer.id, option_id)
        
        logger.info(
            "Answers saved",
            operation="submit_test_service",
            count=len(submission.answers)
        )
        
        submitted_attempt = await submit_attempt(session, attempt.id)
        
        await increment_attempts_count(session, test.id)
        
        await session.commit()
        
        logger.info(
            "Test submission completed successfully",
            operation="submit_test_service",
            attempt_id=attempt.id,
            test_id=test.id
        )
        
        return SubmissionResponse(
            attempt_id=attempt.id,
            test_id=test.id,
            test_title=test.title,
            client_name=attempt.client_name,
            submitted_at=submitted_attempt.submitted_at,
            can_view_report=test.client_can_view_report,
            message="Тест успешно завершен" + (
                ". Отчет доступен для просмотра" if test.client_can_view_report else ""
            )
        )
        
    except SubmissionError:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(
            "Unexpected error during test submission",
            operation="submit_test_service",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
