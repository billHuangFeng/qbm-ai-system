"""
学习服务
提供课程、学习路径、进度管理、练习和测试功能
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal

from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService

logger = logging.getLogger(__name__)


class LearningService:
    """学习服务"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None, cache_service: Optional[CacheService] = None):
        self.db_service = db_service
        self.cache_service = cache_service
    
    # ========== 课程管理 ==========
    
    async def create_course(
        self,
        tenant_id: str,
        title: str,
        description: Optional[str] = None,
        knowledge_ids: Optional[List[str]] = None,
        modules: Optional[List[Dict[str, Any]]] = None,
        estimated_hours: Optional[float] = None,
        difficulty_level: str = 'beginner',
        prerequisites: Optional[List[str]] = None,
        cover_image_url: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建课程"""
        try:
            course_id = str(uuid.uuid4())
            
            course_data = {
                'id': course_id,
                'tenant_id': tenant_id,
                'title': title,
                'description': description,
                'cover_image_url': cover_image_url,
                'knowledge_ids': knowledge_ids or [],
                'modules': modules or [],
                'estimated_hours': estimated_hours,
                'difficulty_level': difficulty_level,
                'prerequisites': prerequisites or [],
                'enrolled_count': 0,
                'completed_count': 0,
                'is_published': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            if self.db_service:
                await self.db_service.insert('learning_courses', course_data)
            
            logger.info(f"创建课程成功: {course_id}, 标题: {title}")
            
            return {
                'success': True,
                'course_id': course_id,
                'course': course_data
            }
            
        except Exception as e:
            logger.error(f"创建课程失败: {e}")
            raise
    
    async def get_course_by_id(self, course_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取课程详情"""
        try:
            if not self.db_service:
                return None
            
            query = "SELECT * FROM learning_courses WHERE id = :id"
            params = {'id': course_id}
            
            if tenant_id:
                query += " AND tenant_id = :tenant_id"
                params['tenant_id'] = tenant_id
            
            course = await self.db_service.fetch_one(query, params)
            
            if course:
                # 获取关联的知识详情
                knowledge_list = []
                if course.get('knowledge_ids'):
                    # 这里应该查询知识详情，暂时简化
                    knowledge_list = course['knowledge_ids']
                course['knowledge_list'] = knowledge_list
            
            return course
            
        except Exception as e:
            logger.error(f"获取课程详情失败: {e}")
            return None
    
    async def list_courses(
        self,
        tenant_id: str,
        is_published: Optional[bool] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取课程列表"""
        try:
            if not self.db_service:
                return {'total': 0, 'courses': []}
            
            conditions = ["tenant_id = :tenant_id"]
            params = {'tenant_id': tenant_id}
            
            if is_published is not None:
                conditions.append("is_published = :is_published")
                params['is_published'] = is_published
            
            if difficulty_level:
                conditions.append("difficulty_level = :difficulty_level")
                params['difficulty_level'] = difficulty_level
            
            where_clause = " AND ".join(conditions)
            
            # 查询总数
            count_query = f"SELECT COUNT(*) as total FROM learning_courses WHERE {where_clause}"
            total_result = await self.db_service.fetch_one(count_query, params)
            total = total_result.get('total', 0) if total_result else 0
            
            # 查询数据
            query = f"""
                SELECT * FROM learning_courses
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
            params['limit'] = limit
            params['offset'] = offset
            
            courses = await self.db_service.fetch_all(query, params)
            
            return {
                'total': total,
                'limit': limit,
                'offset': offset,
                'courses': courses or []
            }
            
        except Exception as e:
            logger.error(f"获取课程列表失败: {e}")
            return {'total': 0, 'courses': []}
    
    # ========== 学习路径管理 ==========
    
    async def create_learning_path(
        self,
        tenant_id: str,
        title: str,
        description: Optional[str] = None,
        objective: Optional[str] = None,
        course_ids: Optional[List[str]] = None,
        target_audience: Optional[str] = None,
        estimated_total_hours: Optional[float] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建学习路径"""
        try:
            path_id = str(uuid.uuid4())
            
            path_data = {
                'id': path_id,
                'tenant_id': tenant_id,
                'title': title,
                'description': description,
                'objective': objective,
                'course_ids': course_ids or [],
                'target_audience': target_audience,
                'estimated_total_hours': estimated_total_hours,
                'enrolled_count': 0,
                'completed_count': 0,
                'is_published': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            if self.db_service:
                await self.db_service.insert('learning_paths', path_data)
            
            logger.info(f"创建学习路径成功: {path_id}, 标题: {title}")
            
            return {
                'success': True,
                'path_id': path_id,
                'path': path_data
            }
            
        except Exception as e:
            logger.error(f"创建学习路径失败: {e}")
            raise
    
    async def get_learning_path_by_id(self, path_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取学习路径详情"""
        try:
            if not self.db_service:
                return None
            
            query = "SELECT * FROM learning_paths WHERE id = :id"
            params = {'id': path_id}
            
            if tenant_id:
                query += " AND tenant_id = :tenant_id"
                params['tenant_id'] = tenant_id
            
            path = await self.db_service.fetch_one(query, params)
            
            if path and path.get('course_ids'):
                # 获取关联的课程详情
                course_list = []
                for course_id in path['course_ids']:
                    course = await self.get_course_by_id(course_id, tenant_id)
                    if course:
                        course_list.append(course)
                path['course_list'] = course_list
            
            return path
            
        except Exception as e:
            logger.error(f"获取学习路径详情失败: {e}")
            return None
    
    # ========== 学习记录管理 ==========
    
    async def start_learning(
        self,
        user_id: str,
        tenant_id: str,
        course_id: Optional[str] = None,
        knowledge_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """开始学习（课程或知识）"""
        try:
            if not course_id and not knowledge_id:
                raise ValueError("必须提供 course_id 或 knowledge_id")
            
            # 检查是否已有学习记录
            existing = await self._get_learning_record(user_id, course_id, knowledge_id)
            
            if existing:
                # 更新最后访问时间
                await self._update_learning_record(
                    existing['id'],
                    {'last_accessed_at': datetime.now()}
                )
                return {
                    'success': True,
                    'record_id': existing['id'],
                    'status': existing['status'],
                    'progress': existing.get('progress_percentage', 0)
                }
            
            # 创建新记录
            record_id = str(uuid.uuid4())
            
            record_data = {
                'id': record_id,
                'user_id': user_id,
                'tenant_id': tenant_id,
                'course_id': course_id,
                'knowledge_id': knowledge_id,
                'status': 'in_progress',
                'progress_percentage': 0.0,
                'started_at': datetime.now(),
                'last_accessed_at': datetime.now(),
                'time_spent_minutes': 0,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            if self.db_service:
                await self.db_service.insert('learning_records', record_data)
            
            logger.info(f"开始学习记录: {record_id}")
            
            return {
                'success': True,
                'record_id': record_id,
                'status': 'in_progress',
                'progress': 0.0
            }
            
        except Exception as e:
            logger.error(f"开始学习失败: {e}")
            raise
    
    async def update_learning_progress(
        self,
        user_id: str,
        course_id: Optional[str] = None,
        knowledge_id: Optional[str] = None,
        progress_percentage: Optional[float] = None,
        time_spent_minutes: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新学习进度"""
        try:
            record = await self._get_learning_record(user_id, course_id, knowledge_id)
            
            if not record:
                raise ValueError("学习记录不存在")
            
            updates = {
                'last_accessed_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            if progress_percentage is not None:
                updates['progress_percentage'] = min(100.0, max(0.0, progress_percentage))
                if updates['progress_percentage'] >= 100:
                    updates['status'] = 'completed'
                    updates['completed_at'] = datetime.now()
            
            if time_spent_minutes is not None:
                updates['time_spent_minutes'] = record.get('time_spent_minutes', 0) + time_spent_minutes
            
            if notes is not None:
                updates['notes'] = notes
            
            await self._update_learning_record(record['id'], updates)
            
            return {
                'success': True,
                'record_id': record['id'],
                'progress': updates.get('progress_percentage', record.get('progress_percentage', 0))
            }
            
        except Exception as e:
            logger.error(f"更新学习进度失败: {e}")
            raise
    
    async def get_learning_progress(
        self,
        user_id: str,
        course_id: Optional[str] = None,
        knowledge_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取学习进度"""
        try:
            record = await self._get_learning_record(user_id, course_id, knowledge_id)
            return record
            
        except Exception as e:
            logger.error(f"获取学习进度失败: {e}")
            return None
    
    # ========== 练习管理 ==========
    
    async def get_exercises(
        self,
        course_id: str,
        knowledge_id: Optional[str] = None,
        exercise_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取练习题"""
        try:
            if not self.db_service:
                return []
            
            conditions = ["course_id = :course_id"]
            params = {'course_id': course_id}
            
            if knowledge_id:
                conditions.append("knowledge_id = :knowledge_id")
                params['knowledge_id'] = knowledge_id
            
            if exercise_type:
                conditions.append("exercise_type = :exercise_type")
                params['exercise_type'] = exercise_type
            
            where_clause = " AND ".join(conditions)
            
            query = f"SELECT * FROM learning_exercises WHERE {where_clause} ORDER BY created_at"
            exercises = await self.db_service.fetch_all(query, params)
            
            # 隐藏正确答案（除非是查看答案模式）
            for ex in exercises:
                if 'correct_answer' in ex:
                    ex['_has_answer'] = True
                    del ex['correct_answer']  # 移除正确答案
            
            return exercises or []
            
        except Exception as e:
            logger.error(f"获取练习题失败: {e}")
            return []
    
    async def submit_exercise_answer(
        self,
        exercise_id: str,
        user_id: str,
        answer: Any
    ) -> Dict[str, Any]:
        """提交练习答案"""
        try:
            if not self.db_service:
                return {'success': False, 'message': '数据库服务未初始化'}
            
            # 获取练习题
            query = "SELECT * FROM learning_exercises WHERE id = :id"
            exercise = await self.db_service.fetch_one(query, {'id': exercise_id})
            
            if not exercise:
                raise ValueError("练习题不存在")
            
            correct_answer = exercise.get('correct_answer')
            is_correct = self._check_answer(answer, correct_answer, exercise.get('exercise_type'))
            
            return {
                'success': True,
                'is_correct': is_correct,
                'explanation': exercise.get('explanation'),
                'correct_answer': correct_answer if is_correct else None  # 答对才显示答案
            }
            
        except Exception as e:
            logger.error(f"提交练习答案失败: {e}")
            raise
    
    # ========== 测试管理 ==========
    
    async def get_test_by_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """获取课程的测试"""
        try:
            if not self.db_service:
                return None
            
            query = "SELECT * FROM learning_tests WHERE course_id = :course_id ORDER BY created_at DESC LIMIT 1"
            test = await self.db_service.fetch_one(query, {'course_id': course_id})
            
            if test:
                # 获取练习题（不包含答案）
                exercise_ids = test.get('exercise_ids', [])
                exercises = []
                for ex_id in exercise_ids:
                    ex_query = "SELECT id, title, description, exercise_type, question_content, options, difficulty_level, points FROM learning_exercises WHERE id = :id"
                    ex = await self.db_service.fetch_one(ex_query, {'id': ex_id})
                    if ex:
                        exercises.append(ex)
                test['exercises'] = exercises
            
            return test
            
        except Exception as e:
            logger.error(f"获取测试失败: {e}")
            return None
    
    async def submit_test(
        self,
        test_id: str,
        user_id: str,
        tenant_id: str,
        answers: Dict[str, Any],  # {exercise_id: answer}
        time_spent_minutes: int
    ) -> Dict[str, Any]:
        """提交测试"""
        try:
            if not self.db_service:
                return {'success': False, 'message': '数据库服务未初始化'}
            
            # 获取测试
            test = await self.db_service.fetch_one(
                "SELECT * FROM learning_tests WHERE id = :id",
                {'id': test_id}
            )
            
            if not test:
                raise ValueError("测试不存在")
            
            exercise_ids = test.get('exercise_ids', [])
            total_points = 0
            max_points = 0
            answer_details = []
            
            # 评分
            for ex_id in exercise_ids:
                ex = await self.db_service.fetch_one(
                    "SELECT * FROM learning_exercises WHERE id = :id",
                    {'id': ex_id}
                )
                if not ex:
                    continue
                
                points = ex.get('points', 10)
                max_points += points
                
                user_answer = answers.get(ex_id)
                correct_answer = ex.get('correct_answer')
                is_correct = self._check_answer(user_answer, correct_answer, ex.get('exercise_type'))
                
                if is_correct:
                    total_points += points
                
                answer_details.append({
                    'exercise_id': ex_id,
                    'answer': user_answer,
                    'is_correct': is_correct,
                    'points': points if is_correct else 0,
                    'max_points': points
                })
            
            # 计算分数
            percentage = (total_points / max_points * 100) if max_points > 0 else 0
            passing_score = test.get('passing_score', 60.0)
            passed = percentage >= passing_score
            
            # 保存测试记录
            test_record = {
                'id': str(uuid.uuid4()),
                'test_id': test_id,
                'user_id': user_id,
                'tenant_id': tenant_id,
                'score': float(total_points),
                'max_score': float(max_points),
                'percentage': float(percentage),
                'passed': passed,
                'answers': answer_details,
                'attempt_number': 1,  # 应该查询之前的尝试次数
                'started_at': datetime.now(),
                'submitted_at': datetime.now(),
                'time_spent_minutes': time_spent_minutes,
                'created_at': datetime.now()
            }
            
            await self.db_service.insert('learning_test_records', test_record)
            
            return {
                'success': True,
                'test_record_id': test_record['id'],
                'score': total_points,
                'max_score': max_points,
                'percentage': percentage,
                'passed': passed,
                'passing_score': passing_score,
                'answers': answer_details
            }
            
        except Exception as e:
            logger.error(f"提交测试失败: {e}")
            raise
    
    # ========== 私有辅助方法 ==========
    
    async def _get_learning_record(
        self,
        user_id: str,
        course_id: Optional[str] = None,
        knowledge_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取学习记录"""
        try:
            if not self.db_service:
                return None
            
            conditions = ["user_id = :user_id"]
            params = {'user_id': user_id}
            
            if course_id:
                conditions.append("course_id = :course_id")
                params['course_id'] = course_id
            
            if knowledge_id:
                conditions.append("knowledge_id = :knowledge_id")
                params['knowledge_id'] = knowledge_id
            
            where_clause = " AND ".join(conditions)
            
            query = f"SELECT * FROM learning_records WHERE {where_clause} ORDER BY created_at DESC LIMIT 1"
            record = await self.db_service.fetch_one(query, params)
            
            return record
            
        except Exception as e:
            logger.error(f"获取学习记录失败: {e}")
            return None
    
    async def _update_learning_record(self, record_id: str, updates: Dict[str, Any]):
        """更新学习记录"""
        try:
            if not self.db_service:
                return
            
            await self.db_service.update(
                'learning_records',
                {'id': record_id},
                updates
            )
            
        except Exception as e:
            logger.error(f"更新学习记录失败: {e}")
    
    def _check_answer(self, user_answer: Any, correct_answer: Any, exercise_type: str) -> bool:
        """检查答案是否正确"""
        try:
            if exercise_type == 'multiple_choice':
                # 选择题：比较答案ID或文本
                if isinstance(user_answer, str) and isinstance(correct_answer, str):
                    return user_answer.strip().lower() == correct_answer.strip().lower()
                elif isinstance(correct_answer, list):
                    return user_answer in correct_answer
                return user_answer == correct_answer
            
            elif exercise_type == 'essay':
                # 论述题：暂时返回True（需要人工评分）
                return True
            
            else:
                # 其他类型：简单比较
                return user_answer == correct_answer
                
        except Exception as e:
            logger.error(f"检查答案失败: {e}")
            return False

