-- =====================================================
-- BMOS系统 - 专家知识库系统表
-- 作用: 存储经过严谨验证的专家知识，用于AI决策和学习
-- 重要性: 提供理论框架，弥补实践经验和网络搜索的不足
-- =====================================================

-- 1. 专家知识主表
CREATE TABLE IF NOT EXISTS expert_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 基本信息
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    knowledge_type VARCHAR(50), -- 'theory', 'methodology', 'case_study', 'tool_template', 'best_practice', 'warning'
    
    -- 分类（混合分类方式：领域+问题类型）
    domain_category VARCHAR(100), -- 领域分类：'business_model', 'cost_optimization', 'resource_allocation', 'capability_enhancement', 'market_strategy', 'product_design'
    problem_type VARCHAR(100), -- 问题类型：'decision_problem', 'optimization_problem', 'risk_problem', 'innovation_problem', 'retrospective_problem'
    tags TEXT[], -- 标签数组
    
    -- 来源与验证
    source_type VARCHAR(50) NOT NULL, -- 'external_import', 'manual_entry'
    source_reference TEXT, -- 来源引用（作者、文献、机构等）
    verified_by UUID REFERENCES user_profiles(id),
    verification_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
    verification_notes TEXT,
    
    -- 应用统计
    applied_count INTEGER DEFAULT 0,
    successful_application_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4), -- 成功率
    relevance_score DECIMAL(5,4) DEFAULT 0.5, -- 相关性得分
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false, -- 是否公开（跨租户可见）
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- 约束
    CONSTRAINT valid_knowledge_type CHECK (knowledge_type IN ('theory', 'methodology', 'case_study', 'tool_template', 'best_practice', 'warning')),
    CONSTRAINT valid_source_type CHECK (source_type IN ('external_import', 'manual_entry')),
    CONSTRAINT valid_verification_status CHECK (verification_status IN ('pending', 'verified', 'rejected')),
    CONSTRAINT valid_relevance_score CHECK (relevance_score >= 0 AND relevance_score <= 1),
    CONSTRAINT valid_success_rate CHECK (success_rate >= 0 AND success_rate <= 1 OR success_rate IS NULL)
);

-- 2. 知识附件表（存储Word/PPT/图片等文件）
CREATE TABLE IF NOT EXISTS knowledge_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_id UUID NOT NULL REFERENCES expert_knowledge(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    file_name VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'word', 'ppt', 'image', 'pdf', 'text'
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    
    extracted_text TEXT, -- 提取的文本内容
    thumbnail_path TEXT, -- 缩略图路径（图片/PPT第一页）
    metadata JSONB, -- 文件元数据（页数、分辨率等）
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_file_type CHECK (file_type IN ('word', 'ppt', 'image', 'pdf', 'text', 'other'))
);

-- 3. 知识应用历史表
CREATE TABLE IF NOT EXISTS knowledge_application_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_id UUID NOT NULL REFERENCES expert_knowledge(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES user_profiles(id),
    
    -- 应用场景
    application_context VARCHAR(200), -- 'decision_making', 'optimization', 'risk_assessment', 'planning', 'retrospective'
    decision_id UUID, -- 关联的决策ID（如果有）
    related_service VARCHAR(100), -- 关联的服务（如 'AI_Decision_Requirements', 'AI_Retrospective'）
    
    -- 应用方式
    application_type VARCHAR(50) NOT NULL, -- 'reference', 'reasoning', 'validation'
    applied_content TEXT, -- 应用的专家知识内容摘要
    reasoning_excerpt TEXT, -- 推理过程摘录
    
    -- 应用结果
    was_helpful BOOLEAN,
    feedback TEXT,
    impact_score DECIMAL(5,4), -- 影响得分
    
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_application_type CHECK (application_type IN ('reference', 'reasoning', 'validation'))
);

-- 4. 学习课程表
CREATE TABLE IF NOT EXISTS learning_courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 课程信息
    title VARCHAR(500) NOT NULL,
    description TEXT,
    cover_image_url TEXT,
    
    -- 知识关联
    knowledge_ids UUID[], -- 关联的知识ID数组
    
    -- 课程结构
    modules JSONB, -- 模块结构 [{module_id, title, order, knowledge_ids, exercises_ids}]
    
    -- 学习设置
    estimated_hours DECIMAL(5,2),
    difficulty_level VARCHAR(20) DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
    prerequisites UUID[], -- 前置课程ID数组
    
    -- 统计
    enrolled_count INTEGER DEFAULT 0,
    completed_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2), -- 平均评分（1-5）
    
    -- 状态
    is_published BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_difficulty_level CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    CONSTRAINT valid_rating CHECK (average_rating >= 0 AND average_rating <= 5 OR average_rating IS NULL)
);

-- 5. 学习路径表
CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    title VARCHAR(500) NOT NULL,
    description TEXT,
    objective TEXT, -- 学习目标
    
    course_ids UUID[], -- 课程ID序列（定义学习顺序）
    
    target_audience VARCHAR(200), -- 目标受众
    estimated_total_hours DECIMAL(6,2),
    
    -- 统计
    enrolled_count INTEGER DEFAULT 0,
    completed_count INTEGER DEFAULT 0,
    average_completion_rate DECIMAL(5,2), -- 平均完成率
    
    is_published BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. 学习记录表
CREATE TABLE IF NOT EXISTS learning_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    course_id UUID REFERENCES learning_courses(id) ON DELETE CASCADE,
    knowledge_id UUID REFERENCES expert_knowledge(id) ON DELETE CASCADE,
    
    -- 学习状态
    status VARCHAR(50) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed', 'paused', 'abandoned'
    progress_percentage DECIMAL(5,2) DEFAULT 0, -- 进度百分比
    
    -- 时间记录
    started_at TIMESTAMP WITH TIME ZONE,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent_minutes INTEGER DEFAULT 0, -- 学习时长（分钟）
    
    -- 学习数据
    notes TEXT, -- 学习笔记
    bookmarks JSONB, -- 书签 [{knowledge_id, position, note}]
    highlights JSONB, -- 高亮标记 [{knowledge_id, text, position}]
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_status CHECK (status IN ('not_started', 'in_progress', 'completed', 'paused', 'abandoned')),
    CONSTRAINT valid_progress CHECK (progress_percentage >= 0 AND progress_percentage <= 100)
);

-- 7. 练习题表
CREATE TABLE IF NOT EXISTS learning_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES learning_courses(id) ON DELETE CASCADE,
    knowledge_id UUID REFERENCES expert_knowledge(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 练习信息
    title VARCHAR(500),
    description TEXT,
    exercise_type VARCHAR(50) NOT NULL, -- 'multiple_choice', 'essay', 'case_analysis', 'application', 'scenario'
    question_content TEXT NOT NULL,
    options JSONB, -- 选择题选项 [{id, text, is_correct}]
    correct_answer JSONB, -- 正确答案（格式取决于题型）
    explanation TEXT, -- 答案解析
    
    -- 难度与权重
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    points INTEGER DEFAULT 10,
    
    -- 应用场景
    application_scenario TEXT, -- 实际应用场景描述
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_exercise_type CHECK (exercise_type IN ('multiple_choice', 'essay', 'case_analysis', 'application', 'scenario')),
    CONSTRAINT valid_exercise_difficulty CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'))
);

-- 8. 测试表
CREATE TABLE IF NOT EXISTS learning_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES learning_courses(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    title VARCHAR(500) NOT NULL,
    description TEXT,
    exercise_ids UUID[], -- 关联的练习题ID数组
    
    -- 测试设置
    time_limit_minutes INTEGER, -- 时间限制（分钟）
    passing_score DECIMAL(5,2) DEFAULT 60.00, -- 及格分数（百分比）
    max_attempts INTEGER DEFAULT 3, -- 最大尝试次数
    
    -- 统计
    total_attempts INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_passing_score CHECK (passing_score >= 0 AND passing_score <= 100),
    CONSTRAINT valid_max_attempts CHECK (max_attempts > 0)
);

-- 9. 测试记录表（记录用户测试结果）
CREATE TABLE IF NOT EXISTS learning_test_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL REFERENCES learning_tests(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 测试结果
    score DECIMAL(5,2),
    max_score DECIMAL(5,2),
    percentage DECIMAL(5,2),
    passed BOOLEAN,
    
    -- 答题详情
    answers JSONB, -- 用户答案 [{exercise_id, answer, is_correct, points}]
    
    -- 尝试信息
    attempt_number INTEGER DEFAULT 1,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    time_spent_minutes INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
-- 专家知识表索引
CREATE INDEX idx_expert_knowledge_tenant_id ON expert_knowledge(tenant_id);
CREATE INDEX idx_expert_knowledge_domain_category ON expert_knowledge(domain_category);
CREATE INDEX idx_expert_knowledge_problem_type ON expert_knowledge(problem_type);
CREATE INDEX idx_expert_knowledge_verification_status ON expert_knowledge(verification_status);
CREATE INDEX idx_expert_knowledge_active ON expert_knowledge(is_active) WHERE is_active = true;
CREATE INDEX idx_expert_knowledge_relevance ON expert_knowledge(relevance_score DESC);
CREATE INDEX idx_expert_knowledge_applied_count ON expert_knowledge(applied_count DESC);
CREATE INDEX idx_expert_knowledge_tags ON expert_knowledge USING GIN(tags);
CREATE INDEX idx_expert_knowledge_created_at ON expert_knowledge(created_at DESC);

-- 全文搜索索引（PostgreSQL）
CREATE INDEX idx_expert_knowledge_fts ON expert_knowledge USING GIN(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(content, ''))
);

-- 知识附件表索引
CREATE INDEX idx_knowledge_attachments_knowledge_id ON knowledge_attachments(knowledge_id);
CREATE INDEX idx_knowledge_attachments_tenant_id ON knowledge_attachments(tenant_id);
CREATE INDEX idx_knowledge_attachments_file_type ON knowledge_attachments(file_type);

-- 知识应用历史表索引
CREATE INDEX idx_knowledge_application_knowledge_id ON knowledge_application_history(knowledge_id);
CREATE INDEX idx_knowledge_application_tenant_id ON knowledge_application_history(tenant_id);
CREATE INDEX idx_knowledge_application_user_id ON knowledge_application_history(user_id);
CREATE INDEX idx_knowledge_application_context ON knowledge_application_history(application_context);
CREATE INDEX idx_knowledge_application_applied_at ON knowledge_application_history(applied_at DESC);

-- 学习课程表索引
CREATE INDEX idx_learning_courses_tenant_id ON learning_courses(tenant_id);
CREATE INDEX idx_learning_courses_published ON learning_courses(is_published) WHERE is_published = true;
CREATE INDEX idx_learning_courses_difficulty ON learning_courses(difficulty_level);
CREATE INDEX idx_learning_courses_knowledge_ids ON learning_courses USING GIN(knowledge_ids);

-- 学习路径表索引
CREATE INDEX idx_learning_paths_tenant_id ON learning_paths(tenant_id);
CREATE INDEX idx_learning_paths_published ON learning_paths(is_published) WHERE is_published = true;
CREATE INDEX idx_learning_paths_course_ids ON learning_paths USING GIN(course_ids);

-- 学习记录表索引
CREATE INDEX idx_learning_records_user_id ON learning_records(user_id);
CREATE INDEX idx_learning_records_tenant_id ON learning_records(tenant_id);
CREATE INDEX idx_learning_records_course_id ON learning_records(course_id);
CREATE INDEX idx_learning_records_knowledge_id ON learning_records(knowledge_id);
CREATE INDEX idx_learning_records_status ON learning_records(status);
CREATE INDEX idx_learning_records_last_accessed ON learning_records(last_accessed_at DESC);

-- 练习题表索引
CREATE INDEX idx_learning_exercises_course_id ON learning_exercises(course_id);
CREATE INDEX idx_learning_exercises_knowledge_id ON learning_exercises(knowledge_id);
CREATE INDEX idx_learning_exercises_tenant_id ON learning_exercises(tenant_id);
CREATE INDEX idx_learning_exercises_type ON learning_exercises(exercise_type);

-- 测试表索引
CREATE INDEX idx_learning_tests_course_id ON learning_tests(course_id);
CREATE INDEX idx_learning_tests_tenant_id ON learning_tests(tenant_id);
CREATE INDEX idx_learning_tests_exercise_ids ON learning_tests USING GIN(exercise_ids);

-- 测试记录表索引
CREATE INDEX idx_learning_test_records_test_id ON learning_test_records(test_id);
CREATE INDEX idx_learning_test_records_user_id ON learning_test_records(user_id);
CREATE INDEX idx_learning_test_records_tenant_id ON learning_test_records(tenant_id);
CREATE INDEX idx_learning_test_records_submitted_at ON learning_test_records(submitted_at DESC);

-- RLS策略
ALTER TABLE expert_knowledge ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON expert_knowledge
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
        OR (is_public = true)  -- 公开知识跨租户可见
    );

ALTER TABLE knowledge_attachments ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON knowledge_attachments
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE knowledge_application_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON knowledge_application_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE learning_courses ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON learning_courses
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE learning_paths ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON learning_paths
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE learning_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON learning_records
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR user_id = auth.uid()  -- 用户可以查看自己的学习记录
        OR has_role(auth.uid(), 'admin')
    );

ALTER TABLE learning_exercises ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON learning_exercises
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE learning_tests ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON learning_tests
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE learning_test_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON learning_test_records
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR user_id = auth.uid()  -- 用户可以查看自己的测试记录
        OR has_role(auth.uid(), 'admin')
    );

-- 注释
COMMENT ON TABLE expert_knowledge IS '专家知识主表 - 存储经过严谨验证的专家知识';
COMMENT ON TABLE knowledge_attachments IS '知识附件表 - 存储Word/PPT/图片等文件';
COMMENT ON TABLE knowledge_application_history IS '知识应用历史表 - 记录专家知识的应用情况';
COMMENT ON TABLE learning_courses IS '学习课程表 - 课程体系和内容组织';
COMMENT ON TABLE learning_paths IS '学习路径表 - 定义结构化学习路径';
COMMENT ON TABLE learning_records IS '学习记录表 - 记录用户的学习进度和笔记';
COMMENT ON TABLE learning_exercises IS '练习题表 - 交互式学习练习题';
COMMENT ON TABLE learning_tests IS '测试表 - 学习测试和评估';
COMMENT ON TABLE learning_test_records IS '测试记录表 - 记录用户测试结果';

