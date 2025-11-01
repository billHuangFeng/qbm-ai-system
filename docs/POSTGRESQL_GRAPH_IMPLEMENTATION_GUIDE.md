# PostgreSQL图数据实现指南

## 📋 概述

本指南详细说明如何在PostgreSQL中实现图数据库特性，以支持"决策制定与执行跟踪系统"的决策关系图谱需求。通过递归CTE、JSONB存储和物化视图等技术，在PostgreSQL中实现复杂的图查询和算法。

---

## 🏗️ 数据模型设计

### 1. 决策节点表 (已存在)
```sql
-- 层级决策表 (已存在)
CREATE TABLE hierarchical_decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_name VARCHAR(200),
    decision_level VARCHAR(20), -- 'strategic', 'tactical', 'operational'
    parent_decision_id UUID,
    decision_date DATE,
    decision_status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. 决策关系表 (新增)
```sql
-- 决策关系表 - 存储决策间的各种关系
CREATE TABLE decision_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    source_decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    target_decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    relationship_type VARCHAR(50) NOT NULL, -- 'parent_child', 'dependency', 'trigger', 'conflict'
    relationship_properties JSONB, -- 存储边的属性
    weight DECIMAL(5,4) DEFAULT 1.0, -- 关系权重
    confidence_score DECIMAL(3,2) DEFAULT 1.0, -- 关系置信度
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_decision_relationships_source ON decision_relationships(source_decision_id);
CREATE INDEX idx_decision_relationships_target ON decision_decision_relationships(target_decision_id);
CREATE INDEX idx_decision_relationships_type ON decision_relationships(relationship_type);
CREATE INDEX idx_decision_relationships_properties ON decision_relationships USING GIN(relationship_properties);
CREATE INDEX idx_decision_relationships_weight ON decision_relationships(weight);
```

### 3. 决策影响表 (新增)
```sql
-- 决策影响表 - 存储决策影响的具体数据
CREATE TABLE decision_impacts (
    impact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    source_decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    target_decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    impact_type VARCHAR(50) NOT NULL, -- 'positive', 'negative', 'neutral'
    impact_value DECIMAL(15,2), -- 影响数值
    impact_percentage DECIMAL(5,2), -- 影响百分比
    impact_description TEXT,
    measurement_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_decision_impacts_source ON decision_impacts(source_decision_id);
CREATE INDEX idx_decision_impacts_target ON decision_impacts(target_decision_id);
CREATE INDEX idx_decision_impacts_type ON decision_impacts(impact_type);
CREATE INDEX idx_decision_impacts_date ON decision_impacts(measurement_date);
```

---

## 🔍 图查询实现

### 1. 递归CTE实现图遍历

#### 1.1 向上追溯查询
```sql
-- 查询决策的所有上级决策
WITH RECURSIVE decision_hierarchy_up AS (
    -- 基础情况：直接上级
    SELECT 
        hd.decision_id,
        hd.decision_name,
        hd.decision_level,
        hd.parent_decision_id,
        1 as depth,
        ARRAY[hd.decision_id] as path
    FROM hierarchical_decisions hd
    WHERE hd.decision_id = $1
    
    UNION ALL
    
    -- 递归情况：间接上级
    SELECT 
        hd.decision_id,
        hd.decision_name,
        hd.decision_level,
        hd.parent_decision_id,
        dhu.depth + 1,
        dhu.path || hd.decision_id
    FROM decision_hierarchy_up dhu
    JOIN hierarchical_decisions hd ON dhu.parent_decision_id = hd.decision_id
    WHERE NOT hd.decision_id = ANY(dhu.path) -- 避免循环
)
SELECT * FROM decision_hierarchy_up ORDER BY depth;
```

#### 1.2 向下追溯查询
```sql
-- 查询决策的所有下级决策
WITH RECURSIVE decision_hierarchy_down AS (
    -- 基础情况：直接下级
    SELECT 
        hd.decision_id,
        hd.decision_name,
        hd.decision_level,
        hd.parent_decision_id,
        1 as depth,
        ARRAY[hd.decision_id] as path
    FROM hierarchical_decisions hd
    WHERE hd.parent_decision_id = $1
    
    UNION ALL
    
    -- 递归情况：间接下级
    SELECT 
        hd.decision_id,
        hd.decision_name,
        hd.decision_level,
        hd.parent_decision_id,
        dhd.depth + 1,
        dhd.path || hd.decision_id
    FROM decision_hierarchy_down dhd
    JOIN hierarchical_decisions hd ON dhd.decision_id = hd.parent_decision_id
    WHERE NOT hd.decision_id = ANY(dhd.path) -- 避免循环
)
SELECT * FROM decision_hierarchy_down ORDER BY depth;
```

#### 1.3 依赖关系查询
```sql
-- 查询决策的所有依赖关系
WITH RECURSIVE decision_dependencies AS (
    -- 基础情况：直接依赖
    SELECT 
        dr.source_decision_id,
        dr.target_decision_id,
        dr.relationship_type,
        dr.weight,
        1 as depth,
        ARRAY[dr.source_decision_id, dr.target_decision_id] as path
    FROM decision_relationships dr
    WHERE dr.source_decision_id = $1
    AND dr.relationship_type = 'dependency'
    
    UNION ALL
    
    -- 递归情况：间接依赖
    SELECT 
        dd.source_decision_id,
        dr.target_decision_id,
        dr.relationship_type,
        dd.weight * dr.weight, -- 累积权重
        dd.depth + 1,
        dd.path || dr.target_decision_id
    FROM decision_dependencies dd
    JOIN decision_relationships dr ON dd.target_decision_id = dr.source_decision_id
    WHERE dr.relationship_type = 'dependency'
    AND NOT dr.target_decision_id = ANY(dd.path) -- 避免循环
    AND dd.depth < 10 -- 限制递归深度
)
SELECT * FROM decision_dependencies ORDER BY depth, weight DESC;
```

### 2. 复杂图查询

#### 2.1 最短路径查询
```sql
-- 查询两个决策间的最短路径
WITH RECURSIVE shortest_path AS (
    -- 基础情况：直接连接
    SELECT 
        dr.source_decision_id,
        dr.target_decision_id,
        dr.relationship_type,
        dr.weight,
        1 as path_length,
        ARRAY[dr.source_decision_id, dr.target_decision_id] as path
    FROM decision_relationships dr
    WHERE dr.source_decision_id = $1
    AND dr.target_decision_id = $2
    
    UNION ALL
    
    -- 递归情况：间接连接
    SELECT 
        sp.source_decision_id,
        dr.target_decision_id,
        dr.relationship_type,
        sp.weight + dr.weight, -- 累积权重
        sp.path_length + 1,
        sp.path || dr.target_decision_id
    FROM shortest_path sp
    JOIN decision_relationships dr ON sp.target_decision_id = dr.source_decision_id
    WHERE NOT dr.target_decision_id = ANY(sp.path) -- 避免循环
    AND sp.path_length < 10 -- 限制路径长度
)
SELECT * FROM shortest_path 
WHERE target_decision_id = $2
ORDER BY path_length, weight
LIMIT 1;
```

#### 2.2 影响传播查询
```sql
-- 查询决策的影响传播路径
WITH RECURSIVE impact_propagation AS (
    -- 基础情况：直接影响
    SELECT 
        dr.source_decision_id,
        dr.target_decision_id,
        dr.weight,
        1 as propagation_depth,
        dr.weight as cumulative_impact,
        ARRAY[dr.source_decision_id, dr.target_decision_id] as path
    FROM decision_relationships dr
    WHERE dr.source_decision_id = $1
    AND dr.relationship_type = 'dependency'
    
    UNION ALL
    
    -- 递归情况：间接影响
    SELECT 
        ip.source_decision_id,
        dr.target_decision_id,
        dr.weight,
        ip.propagation_depth + 1,
        ip.cumulative_impact * dr.weight, -- 累积影响
        ip.path || dr.target_decision_id
    FROM impact_propagation ip
    JOIN decision_relationships dr ON ip.target_decision_id = dr.source_decision_id
    WHERE dr.relationship_type = 'dependency'
    AND NOT dr.target_decision_id = ANY(ip.path) -- 避免循环
    AND ip.propagation_depth < 5 -- 限制传播深度
)
SELECT 
    source_decision_id,
    target_decision_id,
    propagation_depth,
    cumulative_impact,
    CASE 
        WHEN cumulative_impact > 0.8 THEN 'high'
        WHEN cumulative_impact > 0.5 THEN 'medium'
        ELSE 'low'
    END as impact_level,
    path
FROM impact_propagation
ORDER BY cumulative_impact DESC;
```

---

## 📊 物化视图优化

### 1. 决策影响传播物化视图
```sql
-- 创建决策影响传播物化视图
CREATE MATERIALIZED VIEW decision_impact_propagation AS
WITH RECURSIVE impact_calculation AS (
    -- 基础情况：直接影响
    SELECT 
        dr.source_decision_id,
        dr.target_decision_id,
        dr.weight,
        1 as propagation_depth,
        dr.weight as cumulative_impact
    FROM decision_relationships dr
    WHERE dr.relationship_type = 'dependency'
    
    UNION ALL
    
    -- 递归情况：间接影响
    SELECT 
        ic.source_decision_id,
        dr.target_decision_id,
        dr.weight,
        ic.propagation_depth + 1,
        ic.cumulative_impact * dr.weight
    FROM impact_calculation ic
    JOIN decision_relationships dr ON ic.target_decision_id = dr.source_decision_id
    WHERE dr.relationship_type = 'dependency'
    AND ic.propagation_depth < 5 -- 限制递归深度
)
SELECT 
    source_decision_id,
    target_decision_id,
    propagation_depth,
    cumulative_impact,
    CASE 
        WHEN cumulative_impact > 0.8 THEN 'high'
        WHEN cumulative_impact > 0.5 THEN 'medium'
        ELSE 'low'
    END as impact_level
FROM impact_calculation;

-- 创建索引
CREATE INDEX idx_impact_propagation_source ON decision_impact_propagation(source_decision_id);
CREATE INDEX idx_impact_propagation_target ON decision_impact_propagation(target_decision_id);
CREATE INDEX idx_impact_propagation_level ON decision_impact_propagation(impact_level);
CREATE INDEX idx_impact_propagation_depth ON decision_impact_propagation(propagation_depth);
```

### 2. 决策关系统计物化视图
```sql
-- 创建决策关系统计物化视图
CREATE MATERIALIZED VIEW decision_relationship_stats AS
SELECT 
    source_decision_id,
    COUNT(*) as total_relationships,
    COUNT(CASE WHEN relationship_type = 'dependency' THEN 1 END) as dependency_count,
    COUNT(CASE WHEN relationship_type = 'trigger' THEN 1 END) as trigger_count,
    COUNT(CASE WHEN relationship_type = 'conflict' THEN 1 END) as conflict_count,
    AVG(weight) as avg_weight,
    MAX(weight) as max_weight,
    MIN(weight) as min_weight,
    AVG(confidence_score) as avg_confidence
FROM decision_relationships
GROUP BY source_decision_id;

-- 创建索引
CREATE INDEX idx_relationship_stats_source ON decision_relationship_stats(source_decision_id);
CREATE INDEX idx_relationship_stats_count ON decision_relationship_stats(total_relationships);
```

### 3. 物化视图刷新策略
```sql
-- 创建物化视图刷新函数
CREATE OR REPLACE FUNCTION refresh_decision_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY decision_impact_propagation;
    REFRESH MATERIALIZED VIEW CONCURRENTLY decision_relationship_stats;
END;
$$ LANGUAGE plpgsql;

-- 创建定时刷新任务 (需要pg_cron扩展)
SELECT cron.schedule('refresh-decision-views', '0 */6 * * *', 'SELECT refresh_decision_views();');
```

---

## 🧮 图算法实现

### 1. PageRank算法实现
```sql
-- PageRank算法实现
CREATE OR REPLACE FUNCTION calculate_pagerank(
    max_iterations INTEGER DEFAULT 100,
    damping_factor DECIMAL(3,2) DEFAULT 0.85,
    tolerance DECIMAL(10,8) DEFAULT 0.0001
)
RETURNS TABLE(decision_id UUID, pagerank_score DECIMAL(10,8)) AS $$
DECLARE
    iteration INTEGER := 0;
    max_change DECIMAL(10,8) := 1.0;
    total_nodes INTEGER;
BEGIN
    -- 获取总节点数
    SELECT COUNT(*) INTO total_nodes FROM hierarchical_decisions;
    
    -- 创建临时表存储PageRank分数
    CREATE TEMP TABLE pagerank_scores (
        decision_id UUID PRIMARY KEY,
        score DECIMAL(10,8) DEFAULT 1.0 / total_nodes,
        new_score DECIMAL(10,8) DEFAULT 0.0
    );
    
    -- 初始化所有节点
    INSERT INTO pagerank_scores (decision_id, score)
    SELECT decision_id, 1.0 / total_nodes
    FROM hierarchical_decisions;
    
    -- 迭代计算PageRank
    WHILE iteration < max_iterations AND max_change > tolerance LOOP
        iteration := iteration + 1;
        max_change := 0.0;
        
        -- 计算新的PageRank分数
        UPDATE pagerank_scores SET new_score = (
            (1 - damping_factor) / total_nodes + 
            damping_factor * (
                SELECT COALESCE(SUM(ps.score / COALESCE(out_degree.degree, 1)), 0)
                FROM decision_relationships dr
                JOIN pagerank_scores ps ON dr.source_decision_id = ps.decision_id
                LEFT JOIN (
                    SELECT target_decision_id, COUNT(*) as degree
                    FROM decision_relationships
                    GROUP BY target_decision_id
                ) out_degree ON dr.target_decision_id = out_degree.target_decision_id
                WHERE dr.target_decision_id = pagerank_scores.decision_id
            )
        );
        
        -- 计算最大变化
        SELECT MAX(ABS(score - new_score)) INTO max_change
        FROM pagerank_scores;
        
        -- 更新分数
        UPDATE pagerank_scores SET score = new_score;
    END LOOP;
    
    -- 返回结果
    RETURN QUERY
    SELECT ps.decision_id, ps.score
    FROM pagerank_scores ps
    ORDER BY ps.score DESC;
    
    -- 清理临时表
    DROP TABLE pagerank_scores;
END;
$$ LANGUAGE plpgsql;
```

### 2. 最短路径算法实现
```sql
-- 最短路径算法实现
CREATE OR REPLACE FUNCTION find_shortest_path(
    start_decision_id UUID,
    end_decision_id UUID,
    max_depth INTEGER DEFAULT 10
)
RETURNS TABLE(
    path_length INTEGER,
    total_weight DECIMAL(10,4),
    path_nodes UUID[]
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE shortest_path AS (
        -- 基础情况：直接连接
        SELECT 
            1 as path_length,
            dr.weight as total_weight,
            ARRAY[dr.source_decision_id, dr.target_decision_id] as path_nodes
        FROM decision_relationships dr
        WHERE dr.source_decision_id = start_decision_id
        AND dr.target_decision_id = end_decision_id
        
        UNION ALL
        
        -- 递归情况：间接连接
        SELECT 
            sp.path_length + 1,
            sp.total_weight + dr.weight,
            sp.path_nodes || dr.target_decision_id
        FROM shortest_path sp
        JOIN decision_relationships dr ON sp.path_nodes[array_length(sp.path_nodes, 1)] = dr.source_decision_id
        WHERE NOT dr.target_decision_id = ANY(sp.path_nodes) -- 避免循环
        AND sp.path_length < max_depth
    )
    SELECT 
        sp.path_length,
        sp.total_weight,
        sp.path_nodes
    FROM shortest_path sp
    WHERE sp.path_nodes[array_length(sp.path_nodes, 1)] = end_decision_id
    ORDER BY sp.path_length, sp.total_weight
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### 3. 连通性检测算法
```sql
-- 连通性检测算法
CREATE OR REPLACE FUNCTION check_connectivity(
    decision_id_1 UUID,
    decision_id_2 UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    path_exists BOOLEAN := FALSE;
BEGIN
    -- 检查是否存在路径
    SELECT EXISTS(
        WITH RECURSIVE path_search AS (
            SELECT decision_id_1 as current_node, ARRAY[decision_id_1] as visited
            UNION ALL
            SELECT 
                CASE 
                    WHEN dr.source_decision_id = ps.current_node THEN dr.target_decision_id
                    ELSE dr.source_decision_id
                END,
                ps.visited || CASE 
                    WHEN dr.source_decision_id = ps.current_node THEN dr.target_decision_id
                    ELSE dr.source_decision_id
                END
            FROM path_search ps
            JOIN decision_relationships dr ON (
                dr.source_decision_id = ps.current_node OR 
                dr.target_decision_id = ps.current_node
            )
            WHERE NOT (CASE 
                WHEN dr.source_decision_id = ps.current_node THEN dr.target_decision_id
                ELSE dr.source_decision_id
            END) = ANY(ps.visited)
        )
        SELECT 1 FROM path_search WHERE current_node = decision_id_2
    ) INTO path_exists;
    
    RETURN path_exists;
END;
$$ LANGUAGE plpgsql;
```

---

## 🚀 性能优化策略

### 1. 索引优化
```sql
-- 复合索引优化
CREATE INDEX idx_decision_relationships_composite ON decision_relationships(
    source_decision_id, relationship_type, weight
);

-- 部分索引优化
CREATE INDEX idx_decision_relationships_active ON decision_relationships(
    source_decision_id, target_decision_id
) WHERE relationship_type = 'dependency' AND weight > 0.1;

-- 表达式索引优化
CREATE INDEX idx_decision_relationships_weight_desc ON decision_relationships(
    (weight DESC)
) WHERE relationship_type = 'dependency';
```

### 2. 查询优化
```sql
-- 使用EXISTS替代IN
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM hierarchical_decisions hd
WHERE EXISTS (
    SELECT 1 FROM decision_relationships dr
    WHERE dr.source_decision_id = hd.decision_id
    AND dr.relationship_type = 'dependency'
);

-- 使用LIMIT限制递归深度
WITH RECURSIVE limited_path AS (
    SELECT source_decision_id, target_decision_id, 1 as depth
    FROM decision_relationships
    WHERE source_decision_id = $1
    UNION ALL
    SELECT lp.source_decision_id, dr.target_decision_id, lp.depth + 1
    FROM limited_path lp
    JOIN decision_relationships dr ON lp.target_decision_id = dr.source_decision_id
    WHERE lp.depth < 5 -- 限制深度
)
SELECT * FROM limited_path;
```

### 3. 缓存策略
```sql
-- 创建缓存表
CREATE TABLE decision_graph_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 创建缓存清理函数
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM decision_graph_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 创建定时清理任务
SELECT cron.schedule('clean-cache', '0 2 * * *', 'SELECT clean_expired_cache();');
```

---

## 🔧 维护和监控

### 1. 性能监控
```sql
-- 创建性能监控视图
CREATE VIEW decision_graph_performance AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE tablename IN ('decision_relationships', 'hierarchical_decisions', 'decision_impacts');

-- 创建查询性能监控
CREATE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
WHERE query LIKE '%decision_relationships%'
ORDER BY mean_time DESC;
```

### 2. 数据质量检查
```sql
-- 创建数据质量检查函数
CREATE OR REPLACE FUNCTION check_graph_data_quality()
RETURNS TABLE(
    check_name VARCHAR(100),
    check_result VARCHAR(20),
    issue_count INTEGER,
    details TEXT
) AS $$
BEGIN
    -- 检查循环依赖
    RETURN QUERY
    SELECT 
        'circular_dependencies'::VARCHAR(100),
        CASE WHEN COUNT(*) > 0 THEN 'FAIL' ELSE 'PASS' END::VARCHAR(20),
        COUNT(*)::INTEGER,
        'Found circular dependencies in decision relationships'::TEXT
    FROM (
        WITH RECURSIVE cycle_check AS (
            SELECT source_decision_id, target_decision_id, ARRAY[source_decision_id] as path
            FROM decision_relationships
            UNION ALL
            SELECT cc.source_decision_id, dr.target_decision_id, cc.path || dr.target_decision_id
            FROM cycle_check cc
            JOIN decision_relationships dr ON cc.target_decision_id = dr.source_decision_id
            WHERE NOT dr.target_decision_id = ANY(cc.path)
        )
        SELECT 1 FROM cycle_check WHERE target_decision_id = ANY(path)
    ) cycles;
    
    -- 检查孤立节点
    RETURN QUERY
    SELECT 
        'isolated_nodes'::VARCHAR(100),
        CASE WHEN COUNT(*) > 0 THEN 'WARN' ELSE 'PASS' END::VARCHAR(20),
        COUNT(*)::INTEGER,
        'Found isolated decision nodes'::TEXT
    FROM hierarchical_decisions hd
    WHERE NOT EXISTS (
        SELECT 1 FROM decision_relationships dr
        WHERE dr.source_decision_id = hd.decision_id OR dr.target_decision_id = hd.decision_id
    );
    
    -- 检查权重范围
    RETURN QUERY
    SELECT 
        'weight_range'::VARCHAR(100),
        CASE WHEN COUNT(*) > 0 THEN 'WARN' ELSE 'PASS' END::VARCHAR(20),
        COUNT(*)::INTEGER,
        'Found weights outside normal range (0-1)'::TEXT
    FROM decision_relationships
    WHERE weight < 0 OR weight > 1;
END;
$$ LANGUAGE plpgsql;
```

### 3. 自动维护任务
```sql
-- 创建自动维护函数
CREATE OR REPLACE FUNCTION maintain_decision_graph()
RETURNS void AS $$
BEGIN
    -- 刷新物化视图
    REFRESH MATERIALIZED VIEW CONCURRENTLY decision_impact_propagation;
    REFRESH MATERIALIZED VIEW CONCURRENTLY decision_relationship_stats;
    
    -- 更新统计信息
    ANALYZE decision_relationships;
    ANALYZE hierarchical_decisions;
    ANALYZE decision_impacts;
    
    -- 清理过期缓存
    PERFORM clean_expired_cache();
    
    -- 记录维护日志
    INSERT INTO maintenance_log (task_name, completed_at, status)
    VALUES ('decision_graph_maintenance', NOW(), 'completed');
END;
$$ LANGUAGE plpgsql;

-- 创建维护日志表
CREATE TABLE maintenance_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name VARCHAR(100) NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) NOT NULL,
    details TEXT
);

-- 创建定时维护任务
SELECT cron.schedule('maintain-graph', '0 3 * * *', 'SELECT maintain_decision_graph();');
```

---

## 📈 使用示例

### 1. 基本图查询示例
```sql
-- 查询决策A的所有影响路径
SELECT * FROM decision_impact_propagation
WHERE source_decision_id = 'decision-a-uuid'
ORDER BY cumulative_impact DESC;

-- 查询两个决策间的最短路径
SELECT * FROM find_shortest_path(
    'decision-a-uuid'::UUID,
    'decision-b-uuid'::UUID,
    10
);

-- 检查两个决策是否连通
SELECT check_connectivity(
    'decision-a-uuid'::UUID,
    'decision-b-uuid'::UUID
);
```

### 2. 高级分析示例
```sql
-- 计算所有决策的PageRank分数
SELECT * FROM calculate_pagerank(100, 0.85, 0.0001);

-- 查询高影响决策
SELECT 
    hd.decision_name,
    hd.decision_level,
    drs.total_relationships,
    drs.avg_weight
FROM hierarchical_decisions hd
JOIN decision_relationship_stats drs ON hd.decision_id = drs.source_decision_id
WHERE drs.total_relationships > 5
ORDER BY drs.avg_weight DESC;
```

### 3. 性能监控示例
```sql
-- 检查数据质量
SELECT * FROM check_graph_data_quality();

-- 查看慢查询
SELECT * FROM slow_queries LIMIT 10;

-- 查看性能统计
SELECT * FROM decision_graph_performance;
```

---

## 🎯 总结

通过本指南，我们可以在PostgreSQL中实现完整的图数据库特性，包括：

1. **复杂图查询** - 通过递归CTE实现路径查找、影响传播等
2. **图算法** - 实现PageRank、最短路径、连通性检测等算法
3. **性能优化** - 通过物化视图、索引优化、缓存策略提升性能
4. **维护监控** - 通过自动化任务和监控视图确保系统稳定

这个实现方案能够满足"决策制定与执行跟踪系统"对决策关系图谱的所有需求，同时保持与现有PostgreSQL架构的兼容性。

