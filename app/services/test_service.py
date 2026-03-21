from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from datetime import datetime

from app.core.logging_config import get_logger
from app.core.timezone_utils import convert_to_msk_naive
from app.database.crud.test_crud import (
    create_test,
    get_test_by_id,
    get_test_by_token,
    get_tests_by_psychologist,
    update_test,
    delete_test
)
from app.database.crud.test_profile_field_crud import create_profile_field, get_profile_fields_by_test
from app.database.crud.test_section_crud import create_section, get_sections_by_test
from app.database.crud.question_crud import create_question, get_questions_by_test
from app.database.crud.question_option_crud import create_option, get_options_by_question
from app.database.crud.test_metric_crud import create_metric, get_metrics_by_test
from app.database.crud.report_template_crud import create_report_template, get_report_templates_by_test
from app.database.models.tests import Test
from app.database.models.enums import QuestionType, ReportAudience, ProfileFieldType
from app.schemas.test import TestCreate, TestUpdate

logger = get_logger(__name__)


class TestNotFound(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


class TestAccessDenied(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


def generate_test_token() -> str:
    return secrets.token_urlsafe(16)


async def create_test_service(
    session: AsyncSession,
    psychologist_id: int,
    test_data: dict
) -> dict:
    logger.info(
        "Starting test creation with full structure",
        operation="create_test_service",
        psychologist_id=psychologist_id
    )
    
    try:
        token = generate_test_token()
        
        base_data = test_data.get("test", test_data)
        access_until_naive = None
        if base_data.get("access_until"):
            access_until_naive = convert_to_msk_naive(
                datetime.fromisoformat(base_data["access_until"]) 
                if isinstance(base_data["access_until"], str) 
                else base_data["access_until"]
            )
        
        test = await create_test(
            session=session,
            psychologist_id=psychologist_id,
            title=base_data.get("title", "Новый тест"),
            public_link_token=token,
            access_until=access_until_naive,
            client_can_view_report=base_data.get("client_can_view_report", False)
        )
        
        section_id_map = {}
        for section_data in test_data.get("sections", []):
            section = await create_section(
                session=session,
                test_id=test.id,
                title=section_data.get("title"),
                display_order=section_data.get("display_order")
            )
            temp_id = section_data.get("temp_id") or section_data.get("id")
            if temp_id:
                section_id_map[temp_id] = section.id
        
        for pf_data in test_data.get("profile_fields", []):
            await create_profile_field(
                session=session,
                test_id=test.id,
                label=pf_data.get("field_name") or pf_data.get("label"),
                field_type=ProfileFieldType(pf_data.get("field_type")),
                is_required=pf_data.get("is_required", True),
                position=pf_data.get("display_order") or 0
            )
        
        question_id_map = {}
        for q_data in test_data.get("questions", []):
            section_ref = q_data.get("section_id")
            section_id = section_id_map.get(section_ref, section_ref)
            
            question = await create_question(
                session=session,
                test_id=test.id,
                section_id=section_id,
                question_text=q_data.get("question_text"),
                question_type=QuestionType(q_data.get("question_type")),
                is_required=q_data.get("is_required", True),
                display_order=q_data.get("display_order"),
                settings=q_data.get("settings")
            )
            temp_id = q_data.get("temp_id") or q_data.get("id")
            if temp_id:
                question_id_map[temp_id] = question.id
            
            for opt_data in q_data.get("options", []):
                await create_option(
                    session=session,
                    question_id=question.id,
                    option_text=opt_data.get("option_text"),
                    option_value=opt_data.get("option_value"),
                    display_order=opt_data.get("display_order")
                )
        
        for m_data in test_data.get("metrics", []):
            await create_metric(
                session=session,
                test_id=test.id,
                metric_name=m_data.get("metric_name"),
                formula=m_data.get("formula"),
                description=m_data.get("description")
            )
        
        for t_data in test_data.get("report_templates", []):
            await create_report_template(
                session=session,
                test_id=test.id,
                audience=ReportAudience(t_data.get("audience")),
                template_definition=t_data.get("template_definition", {})
            )
        
        await session.commit()
        
        logger.info(
            "Test with full structure created successfully",
            operation="create_test_service",
            test_id=test.id,
            psychologist_id=psychologist_id
        )
        
        return await get_test_by_id_service(session, test.id, psychologist_id)
        
    except Exception as e:
        await session.rollback()
        logger.error(
            "Unexpected error during test creation",
            operation="create_test_service",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def get_tests_by_psychologist_service(
    session: AsyncSession,
    psychologist_id: int,
    skip: int = 0,
    limit: int = 20
) -> tuple[list[Test], int]:
    logger.info(
        "Starting tests list retrieval",
        operation="get_tests_by_psychologist_service",
        psychologist_id=psychologist_id,
        skip=skip,
        limit=limit
    )
    
    try:
        tests, total = await get_tests_by_psychologist(session, psychologist_id, skip, limit)
        
        logger.info(
            "Tests list retrieved successfully",
            operation="get_tests_by_psychologist_service",
            psychologist_id=psychologist_id,
            count=len(tests),
            total=total
        )
        
        return tests, total
        
    except Exception as e:
        logger.error(
            "Unexpected error during tests list retrieval",
            operation="get_tests_by_psychologist_service",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def get_test_by_id_service(
    session: AsyncSession,
    test_id: int,
    psychologist_id: int
) -> dict:
    logger.info(
        "Starting test retrieval with full structure",
        operation="get_test_by_id_service",
        test_id=test_id,
        psychologist_id=psychologist_id
    )
    
    try:
        test = await get_test_by_id(session, test_id)
        
        if not test:
            logger.warning(
                "Test not found",
                operation="get_test_by_id_service",
                test_id=test_id,
                reason="test_not_found"
            )
            raise TestNotFound("test_id", f"Тест с ID {test_id} не найден")
        
        if test.psychologist_id != psychologist_id:
            logger.warning(
                "Test access denied",
                operation="get_test_by_id_service",
                test_id=test_id,
                psychologist_id=psychologist_id,
                test_owner_id=test.psychologist_id,
                reason="access_denied"
            )
            raise TestAccessDenied("test_id", "У вас нет доступа к этому тесту")
        
        profile_fields = await get_profile_fields_by_test(session, test_id)
        sections = await get_sections_by_test(session, test_id)
        questions = await get_questions_by_test(session, test_id)
        metrics = await get_metrics_by_test(session, test_id)
        templates = await get_report_templates_by_test(session, test_id)
        
        questions_with_options = []
        for question in questions:
            options = await get_options_by_question(session, question.id)
            questions_with_options.append({
                "id": question.id,
                "section_id": question.section_id,
                "question_text": question.text,
                "question_type": question.type.value,
                "is_required": True,
                "display_order": question.position,
                "settings": question.settings_json,
                "options": [
                    {
                        "id": opt.id,
                        "option_text": opt.text,
                        "option_value": opt.position,
                        "display_order": opt.position
                    }
                    for opt in options
                ]
            })
        
        result = {
            "id": test.id,
            "title": test.title,
            "public_link_token": test.public_link_token,
            "access_until": test.access_until.isoformat() if test.access_until else None,
            "client_can_view_report": test.client_can_view_report,
            "attempts_count": test.attempts_count,
            "profile_fields": [
                {
                    "id": pf.id,
                    "field_name": pf.label,
                    "field_type": pf.type.value,
                    "is_required": pf.is_required,
                    "display_order": pf.position
                }
                for pf in profile_fields
            ],
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    "display_order": s.position
                }
                for s in sections
            ],
            "questions": questions_with_options,
            "metrics": [
                {
                    "id": m.id,
                    "metric_name": m.metric_name,
                    "formula": m.formula,
                    "description": m.description
                }
                for m in metrics
            ],
            "report_templates": [
                {
                    "id": t.id,
                    "audience": t.audience.value,
                    "template_definition": t.template_definition
                }
                for t in templates
            ]
        }
        
        logger.info(
            "Test with full structure retrieved successfully",
            operation="get_test_by_id_service",
            test_id=test.id
        )
        
        return result
        
    except (TestNotFound, TestAccessDenied):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during test retrieval",
            operation="get_test_by_id_service",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def update_test_service(
    session: AsyncSession,
    test_id: int,
    psychologist_id: int,
    test_data: TestUpdate
) -> Test:
    logger.info(
        "Starting test update",
        operation="update_test_service",
        test_id=test_id,
        psychologist_id=psychologist_id
    )
    
    try:
        test = await get_test_by_id(session, test_id)
        
        if not test:
            logger.warning(
                "Test not found",
                operation="update_test_service",
                test_id=test_id,
                reason="test_not_found"
            )
            raise TestNotFound("test_id", f"Тест с ID {test_id} не найден")
        
        if test.psychologist_id != psychologist_id:
            logger.warning(
                "Test access denied",
                operation="update_test_service",
                test_id=test_id,
                psychologist_id=psychologist_id,
                reason="access_denied"
            )
            raise TestAccessDenied("test_id", "У вас нет доступа к этому тесту")
        
        # Получаем только те поля, которые были явно переданы
        update_data = test_data.model_dump(exclude_unset=True)
        
        # Конвертируем access_until если он был передан
        if 'access_until' in update_data:
            update_data['access_until'] = convert_to_msk_naive(update_data['access_until'])
        
        updated_test = await update_test(
            session=session,
            test_id=test_id,
            **update_data
        )
        
        await session.commit()
        await session.refresh(updated_test)
        
        logger.info(
            "Test updated successfully",
            operation="update_test_service",
            test_id=test_id
        )
        
        return updated_test
        
    except (TestNotFound, TestAccessDenied):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during test update",
            operation="update_test_service",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def delete_test_service(
    session: AsyncSession,
    test_id: int,
    psychologist_id: int
) -> bool:
    logger.info(
        "Starting test deletion",
        operation="delete_test_service",
        test_id=test_id,
        psychologist_id=psychologist_id
    )
    
    try:
        test = await get_test_by_id(session, test_id)
        
        if not test:
            logger.warning(
                "Test not found",
                operation="delete_test_service",
                test_id=test_id,
                reason="test_not_found"
            )
            raise TestNotFound("test_id", f"Тест с ID {test_id} не найден")
        
        if test.psychologist_id != psychologist_id:
            logger.warning(
                "Test access denied",
                operation="delete_test_service",
                test_id=test_id,
                psychologist_id=psychologist_id,
                reason="access_denied"
            )
            raise TestAccessDenied("test_id", "У вас нет доступа к этому тесту")
        
        deleted = await delete_test(session, test_id)
        
        await session.commit()
        
        logger.info(
            "Test deleted successfully",
            operation="delete_test_service",
            test_id=test_id
        )
        
        return deleted
        
    except (TestNotFound, TestAccessDenied):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during test deletion",
            operation="delete_test_service",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def export_test_service(
    session: AsyncSession,
    test_id: int,
    psychologist_id: int
) -> dict:
    logger.info(
        "Starting test export",
        operation="export_test_service",
        test_id=test_id,
        psychologist_id=psychologist_id
    )
    
    try:
        test = await get_test_by_id(session, test_id)
        
        if not test:
            logger.warning(
                "Test not found",
                operation="export_test_service",
                test_id=test_id,
                reason="test_not_found"
            )
            raise TestNotFound("test_id", f"Тест с ID {test_id} не найден")
        
        if test.psychologist_id != psychologist_id:
            logger.warning(
                "Test access denied",
                operation="export_test_service",
                test_id=test_id,
                psychologist_id=psychologist_id,
                reason="access_denied"
            )
            raise TestAccessDenied("test_id", "У вас нет доступа к этому тесту")
        
        profile_fields = await get_profile_fields_by_test(session, test_id)
        sections = await get_sections_by_test(session, test_id)
        questions = await get_questions_by_test(session, test_id)
        metrics = await get_metrics_by_test(session, test_id)
        templates = await get_report_templates_by_test(session, test_id)
        
        all_options = []
        for question in questions:
            options = await get_options_by_question(session, question.id)
            all_options.extend(options)
        
        export_data = {
            "test": {
                "title": test.title,
                "access_until": test.access_until.isoformat() if test.access_until else None,
                "client_can_view_report": test.client_can_view_report
            },
            "profile_fields": [
                {
                    "field_name": pf.label,
                    "field_type": pf.type.value,
                    "is_required": pf.is_required,
                    "display_order": pf.position
                }
                for pf in profile_fields
            ],
            "sections": [
                {
                    "title": s.title,
                    "display_order": s.position
                }
                for s in sections
            ],
            "questions": [
                {
                    "section_id_ref": q.section_id,
                    "question_text": q.text,
                    "question_type": q.type.value,
                    "is_required": True,
                    "display_order": q.position,
                    "settings": q.settings_json
                }
                for q in questions
            ],
            "question_options": [
                {
                    "question_id_ref": opt.question_id,
                    "option_text": opt.text,
                    "option_value": opt.position,
                    "display_order": opt.position
                }
                for opt in all_options
            ],
            "metrics": [
                {
                    "metric_name": m.metric_name,
                    "formula": m.formula,
                    "description": m.description
                }
                for m in metrics
            ],
            "report_templates": [
                {
                    "audience": t.audience.value,
                    "template_definition": t.template_definition
                }
                for t in templates
            ]
        }
        
        logger.info(
            "Test exported successfully",
            operation="export_test_service",
            test_id=test_id
        )
        
        return export_data
        
    except (TestNotFound, TestAccessDenied):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during test export",
            operation="export_test_service",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def import_test_service(
    session: AsyncSession,
    psychologist_id: int,
    import_data: dict
) -> Test:
    logger.info(
        "Starting test import",
        operation="import_test_service",
        psychologist_id=psychologist_id
    )
    
    try:
        if "data" in import_data and "status" in import_data:
            import_data = import_data["data"]
        
        test_data = import_data.get("test", {})
        token = generate_test_token()
        
        title = test_data.get("title")
        if not title:
            title = "Импортированный тест"
        
        access_until_str = test_data.get("access_until")
        access_until = None
        if access_until_str:
            access_until = datetime.fromisoformat(access_until_str)
            access_until = convert_to_msk_naive(access_until)
        
        test = await create_test(
            session=session,
            psychologist_id=psychologist_id,
            title=title,
            public_link_token=token,
            access_until=access_until,
            client_can_view_report=test_data.get("client_can_view_report", False)
        )
        
        section_id_map = {}
        for section_data in import_data.get("sections", []):
            section = await create_section(
                session=session,
                test_id=test.id,
                title=section_data.get("title"),
                display_order=section_data.get("display_order")
            )
            section_id_map[section_data.get("display_order")] = section.id
        
        for pf_data in import_data.get("profile_fields", []):
            await create_profile_field(
                session=session,
                test_id=test.id,
                label=pf_data.get("field_name") or pf_data.get("label"),
                field_type=ProfileFieldType(pf_data.get("field_type")),
                is_required=pf_data.get("is_required", True),
                position=pf_data.get("display_order") or 0
            )
        
        question_id_map = {}
        for q_data in import_data.get("questions", []):
            section_ref = q_data.get("section_id_ref")
            section_id = section_id_map.get(section_ref) if section_ref else None
            
            question = await create_question(
                session=session,
                test_id=test.id,
                section_id=section_id,
                question_text=q_data.get("question_text"),
                question_type=QuestionType(q_data.get("question_type")),
                is_required=q_data.get("is_required", True),
                display_order=q_data.get("display_order"),
                settings=q_data.get("settings")
            )
            question_id_map[q_data.get("display_order")] = question.id
        
        for opt_data in import_data.get("question_options", []):
            question_ref = opt_data.get("question_id_ref")
            question_id = question_id_map.get(question_ref)
            
            if question_id:
                await create_option(
                    session=session,
                    question_id=question_id,
                    option_text=opt_data.get("option_text"),
                    option_value=opt_data.get("option_value"),
                    display_order=opt_data.get("display_order")
                )
        
        for m_data in import_data.get("metrics", []):
            await create_metric(
                session=session,
                test_id=test.id,
                metric_name=m_data.get("metric_name"),
                formula=m_data.get("formula"),
                description=m_data.get("description")
            )
        
        for t_data in import_data.get("report_templates", []):
            await create_report_template(
                session=session,
                test_id=test.id,
                audience=ReportAudience(t_data.get("audience")),
                template_definition=t_data.get("template_definition", {})
            )
        
        await session.commit()
        
        logger.info(
            "Test imported successfully",
            operation="import_test_service",
            test_id=test.id,
            psychologist_id=psychologist_id
        )
        
        return test
        
    except Exception as e:
        logger.error(
            "Unexpected error during test import",
            operation="import_test_service",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise



async def get_test_by_token_service(
    session: AsyncSession,
    token: str
) -> dict:
    logger.info(
        "Starting public test retrieval by token",
        operation="get_test_by_token_service",
        token=token
    )
    
    try:
        test = await get_test_by_token(session, token)
        
        if not test:
            logger.warning(
                "Test not found by token",
                operation="get_test_by_token_service",
                token=token,
                reason="test_not_found"
            )
            raise TestNotFound("token", f"Тест с токеном {token} не найден")
        
        if test.access_until:
            from app.core.timezone_utils import get_current_msk_time
            now = get_current_msk_time()
            if test.access_until < now:
                logger.warning(
                    "Test access expired",
                    operation="get_test_by_token_service",
                    token=token,
                    access_until=test.access_until.isoformat(),
                    reason="access_expired"
                )
                raise TestAccessDenied("access_until", "Срок доступа к тесту истек")
        
        profile_fields = await get_profile_fields_by_test(session, test.id)
        sections = await get_sections_by_test(session, test.id)
        questions = await get_questions_by_test(session, test.id)
        
        questions_with_options = []
        for question in questions:
            options = await get_options_by_question(session, question.id)
            questions_with_options.append({
                "id": question.id,
                "section_id": question.section_id,
                "question_text": question.text,
                "question_type": question.type.value,
                "is_required": True,
                "display_order": question.position,
                "settings": question.settings_json,
                "options": [
                    {
                        "id": opt.id,
                        "option_text": opt.text,
                        "option_value": opt.position,
                        "display_order": opt.position
                    }
                    for opt in options
                ]
            })
        
        result = {
            "id": test.id,
            "title": test.title,
            "client_can_view_report": test.client_can_view_report,
            "profile_fields": [
                {
                    "id": pf.id,
                    "field_name": pf.label,
                    "field_type": pf.type.value,
                    "is_required": pf.is_required,
                    "display_order": pf.position
                }
                for pf in profile_fields
            ],
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    "display_order": s.position
                }
                for s in sections
            ],
            "questions": questions_with_options
        }
        
        logger.info(
            "Public test retrieved successfully",
            operation="get_test_by_token_service",
            test_id=test.id
        )
        
        return result
        
    except (TestNotFound, TestAccessDenied):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during public test retrieval",
            operation="get_test_by_token_service",
            token=token,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
