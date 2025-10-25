-- ===================================
-- BMOS 核心数据库表结构
-- 创建时间: 2025-01-01
-- ===================================

-- 1. 价值主张维度表 (Value Proposition Tags)
CREATE TABLE IF NOT EXISTS dim_vpt (
  vpt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vpt_name TEXT NOT NULL,
  vpt_category TEXT CHECK (vpt_category IN ('功能型', '情感型', '社会型')),
  vpt_description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE dim_vpt IS '价值主张维度表';
COMMENT ON COLUMN dim_vpt.vpt_category IS '价值主张类别：功能型/情感型/社会型';

-- 2. 产品特性维度表 (Product Feature Tags)
CREATE TABLE IF NOT EXISTS dim_pft (
  pft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pft_name TEXT NOT NULL,
  pft_category TEXT,
  pft_description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE dim_pft IS '产品特性维度表';

-- 3. 客户维度表 (Customer Dimension)
CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_name TEXT NOT NULL,
  customer_segment TEXT,
  region TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE dim_customer IS '客户维度表';
CREATE INDEX idx_dim_customer_segment ON dim_customer(customer_segment);

-- 4. 渠道维度表 (Channel Dimension)
CREATE TABLE IF NOT EXISTS dim_channel (
  channel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_name TEXT NOT NULL,
  channel_type TEXT CHECK (channel_type IN ('媒体', '转化', '门店', '电商')),
  channel_description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE dim_channel IS '渠道维度表';
COMMENT ON COLUMN dim_channel.channel_type IS '渠道类型：媒体/转化/门店/电商';

-- 5. SKU维度表 (SKU Dimension)
CREATE TABLE IF NOT EXISTS dim_sku (
  sku_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sku_name TEXT NOT NULL,
  sku_category TEXT,
  price DECIMAL(15,2) CHECK (price >= 0),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE dim_sku IS 'SKU维度表';
CREATE INDEX idx_dim_sku_category ON dim_sku(sku_category);

-- 6. 订单事实表 (Order Fact)
CREATE TABLE IF NOT EXISTS fact_order (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES dim_customer(customer_id) ON DELETE CASCADE,
  sku_id UUID NOT NULL REFERENCES dim_sku(sku_id) ON DELETE RESTRICT,
  channel_id UUID REFERENCES dim_channel(channel_id) ON DELETE SET NULL,
  order_amount DECIMAL(15,2) NOT NULL CHECK (order_amount >= 0),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  order_date TIMESTAMPTZ NOT NULL,
  order_type TEXT CHECK (order_type IN ('首单', '复购', '追销')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE fact_order IS '订单事实表';
COMMENT ON COLUMN fact_order.order_type IS '订单类型：首单/复购/追销';
CREATE INDEX idx_fact_order_date ON fact_order(order_date DESC);
CREATE INDEX idx_fact_order_customer ON fact_order(customer_id);
CREATE INDEX idx_fact_order_sku ON fact_order(sku_id);

-- 7. 客户声音事实表 (Voice of Customer)
CREATE TABLE IF NOT EXISTS fact_voice (
  voice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES dim_customer(customer_id) ON DELETE CASCADE,
  vpt_id UUID REFERENCES dim_vpt(vpt_id) ON DELETE SET NULL,
  satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 5),
  voice_content TEXT,
  voice_date TIMESTAMPTZ NOT NULL,
  sentiment TEXT CHECK (sentiment IN ('正面', '中性', '负面')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE fact_voice IS '客户声音事实表';
COMMENT ON COLUMN fact_voice.satisfaction_score IS '满意度评分：1-5分';
CREATE INDEX idx_fact_voice_date ON fact_voice(voice_date DESC);
CREATE INDEX idx_fact_voice_customer ON fact_voice(customer_id);

-- 8. 归因分析桥接表 (Attribution Bridge)
CREATE TABLE IF NOT EXISTS bridge_attribution (
  attribution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES fact_order(order_id) ON DELETE CASCADE,
  touchpoint_type TEXT NOT NULL CHECK (touchpoint_type IN ('媒体', '渠道', '活动')),
  touchpoint_id UUID NOT NULL,
  attribution_value DECIMAL(10,6) NOT NULL CHECK (attribution_value BETWEEN 0 AND 1),
  attribution_method TEXT DEFAULT 'shapley',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE bridge_attribution IS '归因分析桥接表';
COMMENT ON COLUMN bridge_attribution.attribution_value IS 'Shapley值：0-1之间';
CREATE INDEX idx_bridge_attribution_order ON bridge_attribution(order_id);
CREATE INDEX idx_bridge_attribution_touchpoint ON bridge_attribution(touchpoint_type, touchpoint_id);

-- 9. VPT-PFT映射桥接表
CREATE TABLE IF NOT EXISTS bridge_vpt_pft (
  bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vpt_id UUID NOT NULL REFERENCES dim_vpt(vpt_id) ON DELETE CASCADE,
  pft_id UUID NOT NULL REFERENCES dim_pft(pft_id) ON DELETE CASCADE,
  correlation DECIMAL(3,2) CHECK (correlation BETWEEN -1 AND 1),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(vpt_id, pft_id)
);

COMMENT ON TABLE bridge_vpt_pft IS 'VPT-PFT映射桥接表';
COMMENT ON COLUMN bridge_vpt_pft.correlation IS '相关性系数：-1到1';

-- ===================================
-- 示例数据插入
-- ===================================

-- 插入示例VPT
INSERT INTO dim_vpt (vpt_name, vpt_category, vpt_description) VALUES
  ('极速交付', '功能型', '24小时内送达'),
  ('品质保证', '功能型', '100%正品保证'),
  ('贴心服务', '情感型', '7x24小时客服支持'),
  ('价格优势', '功能型', '全网最低价保证'),
  ('品牌信赖', '社会型', '行业领先品牌')
ON CONFLICT DO NOTHING;

-- 插入示例PFT
INSERT INTO dim_pft (pft_name, pft_category, pft_description) VALUES
  ('高性能处理器', '性能', 'AI芯片加速'),
  ('长续航电池', '续航', '48小时续航'),
  ('轻薄设计', '外观', '仅重1.2kg'),
  ('高清屏幕', '显示', '2K OLED屏幕'),
  ('快充技术', '充电', '30分钟充电80%')
ON CONFLICT DO NOTHING;

-- 插入示例客户
INSERT INTO dim_customer (customer_name, customer_segment, region) VALUES
  ('张三', '高价值客户', '北京'),
  ('李四', '新客户', '上海'),
  ('王五', '流失客户', '广州')
ON CONFLICT DO NOTHING;

-- 插入示例渠道
INSERT INTO dim_channel (channel_name, channel_type, channel_description) VALUES
  ('抖音', '媒体', '短视频平台'),
  ('小红书', '媒体', '种草社区'),
  ('天猫旗舰店', '转化', '电商平台'),
  ('京东自营', '转化', '电商平台'),
  ('线下门店', '门店', '实体零售')
ON CONFLICT DO NOTHING;
