"""
数据导入服务
提供智能数据导入、格式识别、数据清洗等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException
import io
import logging
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class DataImportService:
    """数据导入服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 支持的文件格式
        self.supported_formats = {
            'csv': ['.csv'],
            'excel': ['.xlsx', '.xls'],
            'json': ['.json'],
            'txt': ['.txt']
        }
        
        # 数据表映射配置
        self.table_mappings = {
            'customers': {
                'required_columns': ['customer_name'],
                'optional_columns': [
                    'customer_code', 'customer_type', 'industry', 'contact_person',
                    'phone', 'email', 'address', 'province', 'city', 'is_vip',
                    'customer_value_score', 'customer_lifetime_value', 'customer_satisfaction',
                    'customer_retention_rate', 'first_contact_date', 'last_contact_date'
                ],
                'data_types': {
                    'customer_code': 'string',
                    'customer_name': 'string',
                    'customer_type': 'string',
                    'industry': 'string',
                    'contact_person': 'string',
                    'phone': 'string',
                    'email': 'string',
                    'address': 'string',
                    'province': 'string',
                    'city': 'string',
                    'is_vip': 'boolean',
                    'customer_value_score': 'float',
                    'customer_lifetime_value': 'float',
                    'customer_satisfaction': 'float',
                    'customer_retention_rate': 'float',
                    'first_contact_date': 'datetime',
                    'last_contact_date': 'datetime'
                }
            },
            'products': {
                'required_columns': ['product_name'],
                'optional_columns': [
                    'product_code', 'product_category', 'product_type', 'description',
                    'base_price', 'cost_price', 'profit_margin', 'quality_score',
                    'customer_satisfaction', 'market_share', 'sales_volume', 'revenue',
                    'launch_date', 'end_of_life_date', 'is_featured', 'status'
                ],
                'data_types': {
                    'product_code': 'string',
                    'product_name': 'string',
                    'product_category': 'string',
                    'product_type': 'string',
                    'description': 'string',
                    'base_price': 'float',
                    'cost_price': 'float',
                    'profit_margin': 'float',
                    'quality_score': 'float',
                    'customer_satisfaction': 'float',
                    'market_share': 'float',
                    'sales_volume': 'float',
                    'revenue': 'float',
                    'launch_date': 'datetime',
                    'end_of_life_date': 'datetime',
                    'is_featured': 'boolean',
                    'status': 'string'
                }
            },
            'financials': {
                'required_columns': ['financial_name', 'amount'],
                'optional_columns': [
                    'financial_type', 'category', 'description', 'transaction_date',
                    'accounting_date', 'due_date', 'exchange_rate', 'variance_amount',
                    'variance_percentage', 'cash_flow_type', 'cash_flow_impact',
                    'tax_amount', 'tax_rate', 'status'
                ],
                'data_types': {
                    'financial_name': 'string',
                    'financial_type': 'string',
                    'category': 'string',
                    'description': 'string',
                    'amount': 'float',
                    'transaction_date': 'datetime',
                    'accounting_date': 'datetime',
                    'due_date': 'datetime',
                    'exchange_rate': 'float',
                    'variance_amount': 'float',
                    'variance_percentage': 'float',
                    'cash_flow_type': 'string',
                    'cash_flow_impact': 'float',
                    'tax_amount': 'float',
                    'tax_rate': 'float',
                    'status': 'string'
                }
            }
        }
    
    async def analyze_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        分析上传的文件
        
        Args:
            file: 上传的文件
            
        Returns:
            文件分析结果
        """
        try:
            # 检查文件格式
            file_format = self._detect_file_format(file.filename)
            if not file_format:
                raise HTTPException(status_code=400, detail="不支持的文件格式")
            
            # 读取文件内容
            content = await file.read()
            
            # 解析文件
            df = await self._parse_file(content, file_format)
            
            # 分析数据结构
            structure_analysis = self._analyze_data_structure(df)
            
            # 识别数据表类型
            table_type = self._identify_table_type(df)
            
            # 分析数据质量
            quality_analysis = self._analyze_data_quality(df)
            
            # 生成导入建议
            import_suggestions = self._generate_import_suggestions(df, table_type)
            
            result = {
                'file_info': {
                    'filename': file.filename,
                    'format': file_format,
                    'size': len(content),
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'structure_analysis': structure_analysis,
                'table_type': table_type,
                'quality_analysis': quality_analysis,
                'import_suggestions': import_suggestions,
                'preview_data': df.head(10).to_dict('records')
            }
            
            self.logger.info(f"文件分析完成: {file.filename}")
            return result
            
        except Exception as e:
            self.logger.error(f"文件分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")
    
    async def import_data(self, file: UploadFile, table_type: str, mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        导入数据
        
        Args:
            file: 上传的文件
            table_type: 目标表类型
            mapping_config: 字段映射配置
            
        Returns:
            导入结果
        """
        try:
            # 检查表类型
            if table_type not in self.table_mappings:
                raise HTTPException(status_code=400, detail="不支持的表类型")
            
            # 读取文件
            content = await file.read()
            file_format = self._detect_file_format(file.filename)
            df = await self._parse_file(content, file_format)
            
            # 应用字段映射
            mapped_df = self._apply_field_mapping(df, mapping_config)
            
            # 数据清洗
            cleaned_df = self._clean_data(mapped_df, table_type)
            
            # 数据验证
            validation_result = self._validate_data(cleaned_df, table_type)
            if not validation_result['is_valid']:
                raise HTTPException(status_code=400, detail=f"数据验证失败: {validation_result['errors']}")
            
            # 转换数据类型
            typed_df = self._convert_data_types(cleaned_df, table_type)
            
            # 生成导入报告
            import_report = self._generate_import_report(typed_df, table_type)
            
            result = {
                'import_report': import_report,
                'data_preview': typed_df.head(5).to_dict('records'),
                'success': True,
                'message': f"成功导入 {len(typed_df)} 条记录到 {table_type} 表"
            }
            
            self.logger.info(f"数据导入完成: {file.filename} -> {table_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"数据导入失败: {e}")
            raise HTTPException(status_code=500, detail=f"数据导入失败: {str(e)}")
    
    def _detect_file_format(self, filename: str) -> Optional[str]:
        """检测文件格式"""
        if not filename:
            return None
        
        file_extension = filename.lower().split('.')[-1]
        
        for format_name, extensions in self.supported_formats.items():
            if f'.{file_extension}' in extensions:
                return format_name
        
        return None
    
    async def _parse_file(self, content: bytes, file_format: str) -> pd.DataFrame:
        """解析文件内容"""
        try:
            if file_format == 'csv':
                # 尝试不同的编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(io.StringIO(content.decode(encoding)))
                        return df
                    except UnicodeDecodeError:
                        continue
                raise ValueError("无法解析CSV文件编码")
            
            elif file_format == 'excel':
                df = pd.read_excel(io.BytesIO(content))
                return df
            
            elif file_format == 'json':
                data = json.loads(content.decode('utf-8'))
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.json_normalize(data)
                return df
            
            elif file_format == 'txt':
                # 尝试解析为CSV格式
                text_content = content.decode('utf-8')
                df = pd.read_csv(io.StringIO(text_content), sep='\t')
                return df
            
            else:
                raise ValueError(f"不支持的文件格式: {file_format}")
                
        except Exception as e:
            self.logger.error(f"文件解析失败: {e}")
            raise
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析数据结构"""
        try:
            structure = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'column_types': df.dtypes.astype(str).to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'has_index': df.index.name is not None,
                'duplicate_rows': df.duplicated().sum()
            }
            
            # 分析每列的数据特征
            column_analysis = {}
            for col in df.columns:
                col_data = df[col]
                column_analysis[col] = {
                    'dtype': str(col_data.dtype),
                    'non_null_count': col_data.count(),
                    'null_count': col_data.isnull().sum(),
                    'null_percentage': (col_data.isnull().sum() / len(df)) * 100,
                    'unique_count': col_data.nunique(),
                    'unique_percentage': (col_data.nunique() / len(df)) * 100
                }
                
                # 数值列统计
                if pd.api.types.is_numeric_dtype(col_data):
                    column_analysis[col].update({
                        'min': col_data.min(),
                        'max': col_data.max(),
                        'mean': col_data.mean(),
                        'std': col_data.std(),
                        'median': col_data.median()
                    })
                
                # 文本列统计
                elif pd.api.types.is_string_dtype(col_data):
                    column_analysis[col].update({
                        'avg_length': col_data.astype(str).str.len().mean(),
                        'max_length': col_data.astype(str).str.len().max(),
                        'min_length': col_data.astype(str).str.len().min()
                    })
            
            structure['column_analysis'] = column_analysis
            return structure
            
        except Exception as e:
            self.logger.error(f"数据结构分析失败: {e}")
            return {}
    
    def _identify_table_type(self, df: pd.DataFrame) -> str:
        """识别数据表类型"""
        try:
            column_names = [col.lower() for col in df.columns]
            
            # 计算每种表类型的匹配分数
            scores = {}
            for table_type, config in self.table_mappings.items():
                score = 0
                total_columns = len(config['required_columns']) + len(config['optional_columns'])
                
                # 必需列匹配
                for req_col in config['required_columns']:
                    if req_col.lower() in column_names:
                        score += 2  # 必需列权重更高
                
                # 可选列匹配
                for opt_col in config['optional_columns']:
                    if opt_col.lower() in column_names:
                        score += 1
                
                # 计算匹配率
                scores[table_type] = score / total_columns
            
            # 返回匹配率最高的表类型
            best_match = max(scores.keys(), key=lambda k: scores[k])
            
            # 如果匹配率太低，返回unknown
            if scores[best_match] < 0.3:
                return 'unknown'
            
            return best_match
            
        except Exception as e:
            self.logger.error(f"表类型识别失败: {e}")
            return 'unknown'
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析数据质量"""
        try:
            quality = {
                'completeness': {},
                'consistency': {},
                'accuracy': {},
                'overall_score': 0
            }
            
            # 完整性分析
            total_cells = len(df) * len(df.columns)
            null_cells = df.isnull().sum().sum()
            completeness_score = (total_cells - null_cells) / total_cells * 100
            quality['completeness'] = {
                'score': completeness_score,
                'null_cells': int(null_cells),
                'total_cells': total_cells
            }
            
            # 一致性分析
            consistency_issues = []
            
            # 检查重复行
            duplicate_rows = df.duplicated().sum()
            if duplicate_rows > 0:
                consistency_issues.append(f"发现 {duplicate_rows} 行重复数据")
            
            # 检查数据类型一致性
            for col in df.columns:
                if df[col].dtype == 'object':
                    # 检查是否应该为数值类型
                    numeric_pattern = r'^-?\d+\.?\d*$'
                    numeric_count = df[col].astype(str).str.match(numeric_pattern).sum()
                    if numeric_count > len(df) * 0.8:
                        consistency_issues.append(f"列 '{col}' 可能应该是数值类型")
            
            consistency_score = max(0, 100 - len(consistency_issues) * 10)
            quality['consistency'] = {
                'score': consistency_score,
                'issues': consistency_issues
            }
            
            # 准确性分析（简化版）
            accuracy_score = 100  # 默认满分，实际应用中需要更复杂的验证逻辑
            quality['accuracy'] = {
                'score': accuracy_score,
                'issues': []
            }
            
            # 计算总体质量分数
            quality['overall_score'] = (completeness_score + consistency_score + accuracy_score) / 3
            
            return quality
            
        except Exception as e:
            self.logger.error(f"数据质量分析失败: {e}")
            return {'overall_score': 0}
    
    def _generate_import_suggestions(self, df: pd.DataFrame, table_type: str) -> List[Dict[str, Any]]:
        """生成导入建议"""
        try:
            suggestions = []
            
            if table_type == 'unknown':
                suggestions.append({
                    'type': 'warning',
                    'message': '无法自动识别数据表类型，请手动选择',
                    'action': 'manual_selection'
                })
                return suggestions
            
            # 获取表配置
            table_config = self.table_mappings[table_type]
            required_columns = table_config['required_columns']
            optional_columns = table_config['optional_columns']
            
            # 检查必需列
            missing_required = []
            for req_col in required_columns:
                if req_col.lower() not in [col.lower() for col in df.columns]:
                    missing_required.append(req_col)
            
            if missing_required:
                suggestions.append({
                    'type': 'error',
                    'message': f'缺少必需列: {", ".join(missing_required)}',
                    'action': 'add_required_columns'
                })
            
            # 检查数据质量
            null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if null_percentage > 20:
                suggestions.append({
                    'type': 'warning',
                    'message': f'数据缺失率较高 ({null_percentage:.1f}%)，建议检查数据源',
                    'action': 'check_data_source'
                })
            
            # 检查重复数据
            duplicate_rows = df.duplicated().sum()
            if duplicate_rows > 0:
                suggestions.append({
                    'type': 'warning',
                    'message': f'发现 {duplicate_rows} 行重复数据，建议去重',
                    'action': 'remove_duplicates'
                })
            
            # 数据类型建议
            for col in df.columns:
                if df[col].dtype == 'object':
                    # 检查是否应该为日期类型
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']):
                        suggestions.append({
                            'type': 'info',
                            'message': f'列 "{col}" 可能应该转换为日期类型',
                            'action': 'convert_to_datetime'
                        })
                    
                    # 检查是否应该为数值类型
                    elif any(keyword in col.lower() for keyword in ['price', 'amount', 'score', 'rate', 'count']):
                        suggestions.append({
                            'type': 'info',
                            'message': f'列 "{col}" 可能应该转换为数值类型',
                            'action': 'convert_to_numeric'
                        })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"导入建议生成失败: {e}")
            return []
    
    def _apply_field_mapping(self, df: pd.DataFrame, mapping_config: Dict[str, Any]) -> pd.DataFrame:
        """应用字段映射"""
        try:
            mapped_df = df.copy()
            
            # 重命名列
            if 'column_mapping' in mapping_config:
                column_mapping = mapping_config['column_mapping']
                mapped_df = mapped_df.rename(columns=column_mapping)
            
            # 选择需要的列
            if 'selected_columns' in mapping_config:
                selected_columns = mapping_config['selected_columns']
                mapped_df = mapped_df[selected_columns]
            
            return mapped_df
            
        except Exception as e:
            self.logger.error(f"字段映射应用失败: {e}")
            raise
    
    def _clean_data(self, df: pd.DataFrame, table_type: str) -> pd.DataFrame:
        """清洗数据"""
        try:
            cleaned_df = df.copy()
            
            # 移除完全空白的行
            cleaned_df = cleaned_df.dropna(how='all')
            
            # 移除重复行
            cleaned_df = cleaned_df.drop_duplicates()
            
            # 清理字符串列
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    # 去除首尾空格
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                    # 将空字符串转换为NaN
                    cleaned_df[col] = cleaned_df[col].replace('', np.nan)
            
            return cleaned_df
            
        except Exception as e:
            self.logger.error(f"数据清洗失败: {e}")
            raise
    
    def _validate_data(self, df: pd.DataFrame, table_type: str) -> Dict[str, Any]:
        """验证数据"""
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 获取表配置
            table_config = self.table_mappings[table_type]
            required_columns = table_config['required_columns']
            
            # 检查必需列
            for req_col in required_columns:
                if req_col not in df.columns:
                    validation_result['errors'].append(f"缺少必需列: {req_col}")
                    validation_result['is_valid'] = False
            
            # 检查数据完整性
            for req_col in required_columns:
                if req_col in df.columns:
                    null_count = df[req_col].isnull().sum()
                    if null_count > 0:
                        validation_result['warnings'].append(f"必需列 '{req_col}' 有 {null_count} 个空值")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"数据验证失败: {e}")
            return {'is_valid': False, 'errors': [str(e)], 'warnings': []}
    
    def _convert_data_types(self, df: pd.DataFrame, table_type: str) -> pd.DataFrame:
        """转换数据类型"""
        try:
            typed_df = df.copy()
            table_config = self.table_mappings[table_type]
            data_types = table_config['data_types']
            
            for col, expected_type in data_types.items():
                if col in typed_df.columns:
                    try:
                        if expected_type == 'float':
                            typed_df[col] = pd.to_numeric(typed_df[col], errors='coerce')
                        elif expected_type == 'datetime':
                            typed_df[col] = pd.to_datetime(typed_df[col], errors='coerce')
                        elif expected_type == 'boolean':
                            typed_df[col] = typed_df[col].astype(bool)
                        elif expected_type == 'string':
                            typed_df[col] = typed_df[col].astype(str)
                    except Exception as e:
                        self.logger.warning(f"列 '{col}' 类型转换失败: {e}")
            
            return typed_df
            
        except Exception as e:
            self.logger.error(f"数据类型转换失败: {e}")
            raise
    
    def _generate_import_report(self, df: pd.DataFrame, table_type: str) -> Dict[str, Any]:
        """生成导入报告"""
        try:
            report = {
                'table_type': table_type,
                'total_records': len(df),
                'successful_records': len(df),
                'failed_records': 0,
                'import_timestamp': datetime.now().isoformat(),
                'data_summary': {
                    'columns': len(df.columns),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                    'null_values': df.isnull().sum().sum()
                }
            }
            
            # 按列统计
            column_stats = {}
            for col in df.columns:
                column_stats[col] = {
                    'non_null_count': df[col].count(),
                    'null_count': df[col].isnull().sum(),
                    'unique_count': df[col].nunique(),
                    'data_type': str(df[col].dtype)
                }
            
            report['column_stats'] = column_stats
            return report
            
        except Exception as e:
            self.logger.error(f"导入报告生成失败: {e}")
            return {}
