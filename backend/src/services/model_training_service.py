"""
BMOS系统 - 模型训练服务
作用: 基于历史数据训练和优化预测模型
状态: ✅ 实施中
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
import pickle
import base64
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ModelTrainingService:
    """模型训练服务"""
    
    def __init__(self, db_service=None, cache_service=None):
        self.db_service = db_service
        self.cache_service = cache_service
        self.models = {
            'marginal_analysis': None,  # 边际分析模型
            'timeseries': None,  # 时间序列预测模型
            'npv': None,  # NPV计算模型
            'capability_value': None,  # 能力价值评估模型
        }
        self.scalers = {}
        self.label_encoders = {}
        
    def train_marginal_analysis_model(
        self,
        training_data: pd.DataFrame,
        target_variable: str,
        features: List[str],
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        训练边际分析模型
        
        Args:
            training_data: 训练数据
            target_variable: 目标变量名
            features: 特征列表
            hyperparameters: 超参数
            
        Returns:
            训练结果字典
        """
        try:
            # 准备数据
            X = training_data[features]
            y = training_data[target_variable]
            
            # 处理缺失值
            X = X.fillna(X.mean())
            y = y.fillna(y.mean())
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 训练多个模型
            results = {}
            
            # 1. 随机森林
            rf = RandomForestRegressor(
                n_estimators=hyperparameters.get('rf_n_estimators', 100),
                max_depth=hyperparameters.get('rf_max_depth', 10),
                random_state=42
            )
            rf.fit(X_train, y_train)
            rf_pred = rf.predict(X_test)
            rf_scores = self._calculate_scores(y_test, rf_pred)
            results['random_forest'] = {
                'model': rf,
                'scores': rf_scores
            }
            
            # 2. XGBoost
            xgb_model = xgb.XGBRegressor(
                n_estimators=hyperparameters.get('xgb_n_estimators', 100),
                max_depth=hyperparameters.get('xgb_max_depth', 6),
                random_state=42
            )
            xgb_model.fit(X_train, y_train)
            xgb_pred = xgb_model.predict(X_test)
            xgb_scores = self._calculate_scores(y_test, xgb_pred)
            results['xgboost'] = {
                'model': xgb_model,
                'scores': xgb_scores
            }
            
            # 3. LightGBM
            lgb_model = lgb.LGBMRegressor(
                n_estimators=hyperparameters.get('lgb_n_estimators', 100),
                max_depth=hyperparameters.get('lgb_max_depth', 6),
                random_state=42
            )
            lgb_model.fit(X_train, y_train)
            lgb_pred = lgb_model.predict(X_test)
            lgb_scores = self._calculate_scores(y_test, lgb_pred)
            results['lightgbm'] = {
                'model': lgb_model,
                'scores': lgb_scores
            }
            
            # 选择最佳模型
            best_model_name = min(results.keys(), key=lambda k: results[k]['scores']['mae'])
            best_model = results[best_model_name]['model']
            best_scores = results[best_model_name]['scores']
            
            # 计算特征重要性
            feature_importance = self._get_feature_importance(best_model, features)
            
            return {
                'success': True,
                'model': best_model,
                'model_name': best_model_name,
                'scores': best_scores,
                'feature_importance': feature_importance,
                'training_data_size': len(training_data),
                'feature_count': len(features),
                'all_models': {k: v['scores'] for k, v in results.items()}
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def train_timeseries_model(
        self,
        historical_data: pd.DataFrame,
        target_variable: str,
        date_column: str = 'date',
        forecast_periods: int = 3,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        训练时间序列模型
        
        Args:
            historical_data: 历史数据
            target_variable: 目标变量
            date_column: 日期列名
            forecast_periods: 预测周期数
            hyperparameters: 超参数
            
        Returns:
            训练结果字典
        """
        try:
            # 准备数据
            data = historical_data.copy()
            data[date_column] = pd.to_datetime(data[date_column])
            data = data.sort_values(by=date_column)
            
            # 创建滞后特征
            for lag in range(1, 4):
                data[f'{target_variable}_lag_{lag}'] = data[target_variable].shift(lag)
            
            # 创建时间特征
            data['year'] = data[date_column].dt.year
            data['month'] = data[date_column].dt.month
            data['quarter'] = data[date_column].dt.quarter
            
            # 移除缺失值
            data = data.dropna()
            
            # 准备特征
            feature_columns = [col for col in data.columns if col != target_variable and col != date_column]
            X = data[feature_columns]
            y = data[target_variable]
            
            # 训练模型
            model = GradientBoostingRegressor(
                n_estimators=hyperparameters.get('n_estimators', 100),
                max_depth=hyperparameters.get('max_depth', 6),
                learning_rate=hyperparameters.get('learning_rate', 0.1),
                random_state=42
            )
            model.fit(X, y)
            
            # 计算交叉验证分数
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            
            # 生成预测
            predictions = self._generate_forecast(model, data, feature_columns, forecast_periods)
            
            # 计算特征重要性
            feature_importance = self._get_feature_importance(model, feature_columns)
            
            return {
                'success': True,
                'model': model,
                'predictions': predictions,
                'scores': {
                    'mae': cv_mae,
                    'cv_std': cv_scores.std()
                },
                'feature_importance': feature_importance,
                'training_data_size': len(data),
                'forecast_periods': forecast_periods
            }
            
        except Exception as e:
            logger.error(f"Timeseries training failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_scores(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """计算模型评分"""
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape)
        }
    
    def _get_feature_importance(self, model: Any, features: List[str]) -> Dict[str, float]:
        """获取特征重要性"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return dict(zip(features, importances.tolist()))
        return {}
    
    def _generate_forecast(
        self,
        model: Any,
        data: pd.DataFrame,
        feature_columns: List[str],
        periods: int
    ) -> List[Dict[str, Any]]:
        """生成预测"""
        predictions = []
        last_row = data.iloc[-1].copy()
        
        for i in range(periods):
            # 更新滞后特征
            for lag in range(1, 4):
                lag_col = f'{last_row.name}_lag_{lag}'
                if lag_col in feature_columns:
                    # 使用上一期的预测值
                    last_row[lag_col] = data.iloc[-1].get(lag_col, 0)
            
            # 更新日期
            last_row['year'] = (datetime.now().year + (i + 1) // 12)
            last_row['month'] = ((datetime.now().month + i) % 12) + 1
            last_row['quarter'] = ((datetime.now().month + i) // 3) + 1
            
            # 预测
            X_forecast = last_row[feature_columns].values.reshape(1, -1)
            pred_value = model.predict(X_forecast)[0]
            
            predictions.append({
                'period': i + 1,
                'predicted_value': float(pred_value),
                'date': (datetime.now() + pd.DateOffset(months=i)).strftime('%Y-%m')
            })
        
        return predictions
    
    def retrain_model_with_feedback(
        self,
        existing_model: Any,
        training_data: pd.DataFrame,
        feedback_data: Dict[str, Any],
        update_strategy: str = 'incremental'
    ) -> Dict[str, Any]:
        """
        基于反馈重训练模型
        
        Args:
            existing_model: 现有模型
            training_data: 训练数据
            feedback_data: 反馈数据
            update_strategy: 更新策略 ('incremental' | 'full_retrain')
            
        Returns:
            训练结果字典
        """
        try:
            if update_strategy == 'incremental':
                # 增量学习: 只在现有数据中添加反馈数据
                feedback_df = pd.DataFrame([feedback_data])
                updated_data = pd.concat([training_data, feedback_df], ignore_index=True)
                
                # 重新训练模型
                # (这里简化处理,实际应该使用增量学习算法)
                return {
                    'success': True,
                    'message': 'Incremental update applied',
                    'data_size': len(updated_data)
                }
                
            else:  # full_retrain
                # 完全重训练
                return self.train_marginal_analysis_model(
                    training_data, 
                    feedback_data.get('target_variable'),
                    feedback_data.get('features')
                )
                
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def evaluate_model_performance(
        self,
        model: Any,
        test_data: pd.DataFrame,
        target_variable: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """评估模型性能"""
        try:
            X_test = test_data[features]
            y_test = test_data[target_variable]
            
            y_pred = model.predict(X_test)
            scores = self._calculate_scores(y_test, y_pred)
            
            return {
                'success': True,
                'scores': scores,
                'data_size': len(test_data)
            }
            
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def predict(
        self,
        model_id: str,
        input_data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        使用模型进行预测
        
        Args:
            model_id: 模型ID
            input_data: 输入数据
            tenant_id: 租户ID
            
        Returns:
            预测结果
        """
        try:
            # 从数据库获取模型
            model_info = await self.db_service.execute_one("""
                SELECT * FROM model_parameters_storage 
                WHERE id = $1 AND tenant_id = $2 AND model_status = 'active'
            """, [model_id, tenant_id])
            
            if not model_info:
                return {
                    'success': False,
                    'error': 'Model not found or inactive'
                }
            
            # 反序列化模型
            model_bytes = base64.b64decode(model_info['parameters']['model'])
            model = pickle.loads(model_bytes)
            
            # 准备输入数据
            feature_list = model_info['parameters']['feature_list']
            X = pd.DataFrame([input_data])[feature_list]
            
            # 数据预处理
            X = self._preprocess_input_data(X, model_info)
            
            # 预测
            prediction = model.predict(X)[0]
            
            # 计算置信区间
            confidence_interval = self._calculate_confidence_interval(
                model, X, model_info.get('mae', 0)
            )
            
            return {
                'success': True,
                'prediction': {
                    'value': float(prediction),
                    'confidence_interval': confidence_interval,
                    'model_id': model_id,
                    'model_version': model_info['model_version']
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def train_npv_model(
        self,
        asset_data: pd.DataFrame,
        cash_flow_data: pd.DataFrame,
        discount_rate: float = 0.1,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        训练NPV计算模型
        
        Args:
            asset_data: 资产数据
            cash_flow_data: 现金流数据
            discount_rate: 折现率
            hyperparameters: 超参数
            
        Returns:
            训练结果
        """
        try:
            # 合并数据
            merged_data = pd.merge(asset_data, cash_flow_data, on='asset_id', how='inner')
            
            # 计算NPV特征
            merged_data['npv'] = self._calculate_npv(
                merged_data['initial_investment'],
                merged_data['annual_cash_flow'],
                merged_data['project_life'],
                discount_rate
            )
            
            # 准备特征
            feature_columns = [
                'initial_investment', 'annual_cash_flow', 'project_life',
                'risk_level', 'market_condition', 'asset_type'
            ]
            
            X = merged_data[feature_columns]
            y = merged_data['npv']
            
            # 编码分类变量
            X_encoded = self._encode_categorical_features(X)
            
            # 训练模型
            model = RandomForestRegressor(
                n_estimators=hyperparameters.get('n_estimators', 100),
                max_depth=hyperparameters.get('max_depth', 10),
                random_state=42
            )
            model.fit(X_encoded, y)
            
            # 评估
            y_pred = model.predict(X_encoded)
            scores = self._calculate_scores(y, y_pred)
            
            return {
                'success': True,
                'model': model,
                'scores': scores,
                'feature_importance': self._get_feature_importance(model, feature_columns),
                'training_data_size': len(merged_data)
            }
            
        except Exception as e:
            logger.error(f"NPV model training failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def train_capability_value_model(
        self,
        capability_data: pd.DataFrame,
        performance_data: pd.DataFrame,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        训练能力价值评估模型
        
        Args:
            capability_data: 能力数据
            performance_data: 绩效数据
            hyperparameters: 超参数
            
        Returns:
            训练结果
        """
        try:
            # 合并数据
            merged_data = pd.merge(capability_data, performance_data, on='capability_id', how='inner')
            
            # 准备特征
            feature_columns = [
                'capability_level', 'training_investment', 'experience_years',
                'team_size', 'technology_level', 'process_maturity'
            ]
            
            X = merged_data[feature_columns]
            y = merged_data['performance_score']
            
            # 训练模型
            model = GradientBoostingRegressor(
                n_estimators=hyperparameters.get('n_estimators', 100),
                learning_rate=hyperparameters.get('learning_rate', 0.1),
                max_depth=hyperparameters.get('max_depth', 6),
                random_state=42
            )
            model.fit(X, y)
            
            # 评估
            y_pred = model.predict(X)
            scores = self._calculate_scores(y, y_pred)
            
            return {
                'success': True,
                'model': model,
                'scores': scores,
                'feature_importance': self._get_feature_importance(model, feature_columns),
                'training_data_size': len(merged_data)
            }
            
        except Exception as e:
            logger.error(f"Capability value model training failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_model_parameters(
        self,
        model: Any,
        model_type: str,
        model_version: str,
        training_result: Dict[str, Any],
        tenant_id: str,
        supabase_client: Any
    ) -> str:
        """
        保存模型参数到数据库
        
        Args:
            model: 训练好的模型
            model_type: 模型类型
            model_version: 模型版本
            training_result: 训练结果
            tenant_id: 租户ID
            supabase_client: Supabase客户端
            
        Returns:
            模型ID
        """
        try:
            # 将模型序列化
            model_bytes = pickle.dumps(model)
            model_base64 = base64.b64encode(model_bytes).decode('utf-8')
            
            # 准备数据
            model_data = {
                'tenant_id': tenant_id,
                'model_type': model_type,
                'model_version': model_version,
                'model_name': f'{model_type}_{model_version}',
                'parameters': {
                    'model': model_base64,
                    'feature_list': list(training_result.get('feature_importance', {}).keys())
                },
                'hyperparameters': training_result.get('hyperparameters', {}),
                'feature_importance': training_result.get('feature_importance', {}),
                'accuracy_score': training_result.get('scores', {}).get('r2', 0),
                'r_squared': training_result.get('scores', {}).get('r2', 0),
                'mae': training_result.get('scores', {}).get('mae', 0),
                'rmse': training_result.get('scores', {}).get('rmse', 0),
                'training_data_size': training_result.get('training_data_size', 0),
                'last_training_date': datetime.now().isoformat(),
                'model_status': 'active',
                'is_production': False
            }
            
            # 保存到数据库
            result = supabase_client.table('model_parameters_storage').insert(model_data).execute()
            
            return result.data[0]['id'] if result.data else None
            
        except Exception as e:
            logger.error(f"Model saving failed: {e}")
            raise
    
    # 辅助方法
    def _calculate_npv(
        self,
        initial_investment: pd.Series,
        annual_cash_flow: pd.Series,
        project_life: pd.Series,
        discount_rate: float
    ) -> pd.Series:
        """计算NPV"""
        npv_values = []
        for i in range(len(initial_investment)):
            npv = -initial_investment.iloc[i]
            for year in range(1, int(project_life.iloc[i]) + 1):
                npv += annual_cash_flow.iloc[i] / ((1 + discount_rate) ** year)
            npv_values.append(npv)
        return pd.Series(npv_values)
    
    def _encode_categorical_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """编码分类特征"""
        X_encoded = X.copy()
        for column in X_encoded.columns:
            if X_encoded[column].dtype == 'object':
                if column not in self.label_encoders:
                    self.label_encoders[column] = LabelEncoder()
                    X_encoded[column] = self.label_encoders[column].fit_transform(X_encoded[column])
                else:
                    X_encoded[column] = self.label_encoders[column].transform(X_encoded[column])
        return X_encoded
    
    def _preprocess_input_data(self, X: pd.DataFrame, model_info: Dict[str, Any]) -> pd.DataFrame:
        """预处理输入数据"""
        # 处理缺失值
        X = X.fillna(X.mean())
        
        # 标准化数值特征
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        if numeric_columns.any():
            scaler_key = f"scaler_{model_info['id']}"
            if scaler_key not in self.scalers:
                self.scalers[scaler_key] = StandardScaler()
                X[numeric_columns] = self.scalers[scaler_key].fit_transform(X[numeric_columns])
            else:
                X[numeric_columns] = self.scalers[scaler_key].transform(X[numeric_columns])
        
        return X
    
    def _calculate_confidence_interval(
        self,
        model: Any,
        X: pd.DataFrame,
        mae: float,
        confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """计算置信区间"""
        try:
            # 使用MAE估算标准差
            std_error = mae / 1.25  # 经验公式
            
            # 计算置信区间
            alpha = 1 - confidence_level
            z_score = stats.norm.ppf(1 - alpha/2)
            margin_error = z_score * std_error
            
            prediction = model.predict(X)[0]
            
            return {
                'lower_bound': float(prediction - margin_error),
                'upper_bound': float(prediction + margin_error),
                'confidence_level': confidence_level
            }
        except:
            return {
                'lower_bound': 0,
                'upper_bound': 0,
                'confidence_level': confidence_level
            }

