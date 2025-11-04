export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      alert_rules: {
        Row: {
          alert_type: string | null
          comparison_operator: string | null
          condition_type: string | null
          created_at: string | null
          created_by: string | null
          is_active: boolean | null
          last_triggered_at: string | null
          monitored_metric: string | null
          notification_channels: Json | null
          recipients: Json | null
          rule_id: string
          rule_name: string
          severity_level: string | null
          tenant_id: string | null
          threshold_value: number | null
          updated_at: string | null
        }
        Insert: {
          alert_type?: string | null
          comparison_operator?: string | null
          condition_type?: string | null
          created_at?: string | null
          created_by?: string | null
          is_active?: boolean | null
          last_triggered_at?: string | null
          monitored_metric?: string | null
          notification_channels?: Json | null
          recipients?: Json | null
          rule_id?: string
          rule_name: string
          severity_level?: string | null
          tenant_id?: string | null
          threshold_value?: number | null
          updated_at?: string | null
        }
        Update: {
          alert_type?: string | null
          comparison_operator?: string | null
          condition_type?: string | null
          created_at?: string | null
          created_by?: string | null
          is_active?: boolean | null
          last_triggered_at?: string | null
          monitored_metric?: string | null
          notification_channels?: Json | null
          recipients?: Json | null
          rule_id?: string
          rule_name?: string
          severity_level?: string | null
          tenant_id?: string | null
          threshold_value?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "alert_rules_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      bridge_attribution: {
        Row: {
          attribution_id: string
          attribution_value: number | null
          created_at: string | null
          order_id: string | null
          shapley_value: number | null
          tenant_id: string | null
          touchpoint_id: string | null
          touchpoint_type: string | null
        }
        Insert: {
          attribution_id?: string
          attribution_value?: number | null
          created_at?: string | null
          order_id?: string | null
          shapley_value?: number | null
          tenant_id?: string | null
          touchpoint_id?: string | null
          touchpoint_type?: string | null
        }
        Update: {
          attribution_id?: string
          attribution_value?: number | null
          created_at?: string | null
          order_id?: string | null
          shapley_value?: number | null
          tenant_id?: string | null
          touchpoint_id?: string | null
          touchpoint_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bridge_attribution_order_id_fkey"
            columns: ["order_id"]
            isOneToOne: false
            referencedRelation: "fact_order"
            referencedColumns: ["order_id"]
          },
          {
            foreignKeyName: "bridge_attribution_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      bridge_conv_vpt: {
        Row: {
          bridge_id: string
          conv_channel_id: string | null
          conversion_count: number | null
          created_at: string | null
          tenant_id: string | null
          vpt_id: string | null
        }
        Insert: {
          bridge_id?: string
          conv_channel_id?: string | null
          conversion_count?: number | null
          created_at?: string | null
          tenant_id?: string | null
          vpt_id?: string | null
        }
        Update: {
          bridge_id?: string
          conv_channel_id?: string | null
          conversion_count?: number | null
          created_at?: string | null
          tenant_id?: string | null
          vpt_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bridge_conv_vpt_conv_channel_id_fkey"
            columns: ["conv_channel_id"]
            isOneToOne: false
            referencedRelation: "dim_conv_channel"
            referencedColumns: ["conv_channel_id"]
          },
          {
            foreignKeyName: "bridge_conv_vpt_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "bridge_conv_vpt_vpt_id_fkey"
            columns: ["vpt_id"]
            isOneToOne: false
            referencedRelation: "dim_vpt"
            referencedColumns: ["vpt_id"]
          },
        ]
      }
      bridge_media_vpt: {
        Row: {
          bridge_id: string
          created_at: string | null
          impression_count: number | null
          media_channel_id: string | null
          reach_count: number | null
          tenant_id: string | null
          vpt_id: string | null
        }
        Insert: {
          bridge_id?: string
          created_at?: string | null
          impression_count?: number | null
          media_channel_id?: string | null
          reach_count?: number | null
          tenant_id?: string | null
          vpt_id?: string | null
        }
        Update: {
          bridge_id?: string
          created_at?: string | null
          impression_count?: number | null
          media_channel_id?: string | null
          reach_count?: number | null
          tenant_id?: string | null
          vpt_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bridge_media_vpt_media_channel_id_fkey"
            columns: ["media_channel_id"]
            isOneToOne: false
            referencedRelation: "dim_media_channel"
            referencedColumns: ["media_channel_id"]
          },
          {
            foreignKeyName: "bridge_media_vpt_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "bridge_media_vpt_vpt_id_fkey"
            columns: ["vpt_id"]
            isOneToOne: false
            referencedRelation: "dim_vpt"
            referencedColumns: ["vpt_id"]
          },
        ]
      }
      bridge_sku_pft: {
        Row: {
          bridge_id: string
          created_at: string | null
          pft_id: string | null
          sku_id: string | null
          tenant_id: string | null
          weight: number | null
        }
        Insert: {
          bridge_id?: string
          created_at?: string | null
          pft_id?: string | null
          sku_id?: string | null
          tenant_id?: string | null
          weight?: number | null
        }
        Update: {
          bridge_id?: string
          created_at?: string | null
          pft_id?: string | null
          sku_id?: string | null
          tenant_id?: string | null
          weight?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "bridge_sku_pft_pft_id_fkey"
            columns: ["pft_id"]
            isOneToOne: false
            referencedRelation: "dim_pft"
            referencedColumns: ["pft_id"]
          },
          {
            foreignKeyName: "bridge_sku_pft_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "bridge_sku_pft_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      bridge_vpt_pft: {
        Row: {
          bridge_id: string
          correlation: number | null
          created_at: string | null
          pft_id: string | null
          tenant_id: string | null
          vpt_id: string | null
        }
        Insert: {
          bridge_id?: string
          correlation?: number | null
          created_at?: string | null
          pft_id?: string | null
          tenant_id?: string | null
          vpt_id?: string | null
        }
        Update: {
          bridge_id?: string
          correlation?: number | null
          created_at?: string | null
          pft_id?: string | null
          tenant_id?: string | null
          vpt_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bridge_vpt_pft_pft_id_fkey"
            columns: ["pft_id"]
            isOneToOne: false
            referencedRelation: "dim_pft"
            referencedColumns: ["pft_id"]
          },
          {
            foreignKeyName: "bridge_vpt_pft_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "bridge_vpt_pft_vpt_id_fkey"
            columns: ["vpt_id"]
            isOneToOne: false
            referencedRelation: "dim_vpt"
            referencedColumns: ["vpt_id"]
          },
        ]
      }
      controllable_facts: {
        Row: {
          control_mechanism: string | null
          controllability_level: string | null
          created_at: string | null
          created_by: string | null
          effective_date: string | null
          expiry_date: string | null
          fact_category: string | null
          fact_id: string
          fact_name: string
          fact_type: string | null
          fact_unit: string | null
          fact_value: number | null
          max_value: number | null
          min_value: number | null
          optimal_value: number | null
          related_decisions: Json | null
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          control_mechanism?: string | null
          controllability_level?: string | null
          created_at?: string | null
          created_by?: string | null
          effective_date?: string | null
          expiry_date?: string | null
          fact_category?: string | null
          fact_id?: string
          fact_name: string
          fact_type?: string | null
          fact_unit?: string | null
          fact_value?: number | null
          max_value?: number | null
          min_value?: number | null
          optimal_value?: number | null
          related_decisions?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          control_mechanism?: string | null
          controllability_level?: string | null
          created_at?: string | null
          created_by?: string | null
          effective_date?: string | null
          expiry_date?: string | null
          fact_category?: string | null
          fact_id?: string
          fact_name?: string
          fact_type?: string | null
          fact_unit?: string | null
          fact_value?: number | null
          max_value?: number | null
          min_value?: number | null
          optimal_value?: number | null
          related_decisions?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "controllable_facts_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      cross_tenant_access: {
        Row: {
          access_id: string
          access_level: string | null
          analyst_id: string
          expires_at: string | null
          granted_at: string | null
          granted_by: string | null
          tenant_id: string
        }
        Insert: {
          access_id?: string
          access_level?: string | null
          analyst_id: string
          expires_at?: string | null
          granted_at?: string | null
          granted_by?: string | null
          tenant_id: string
        }
        Update: {
          access_id?: string
          access_level?: string | null
          analyst_id?: string
          expires_at?: string | null
          granted_at?: string | null
          granted_by?: string | null
          tenant_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "cross_tenant_access_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      data_import_log: {
        Row: {
          created_at: string | null
          duplicate_rows: number | null
          error_details: Json | null
          failed_rows: number | null
          import_duration_ms: number | null
          import_type: string | null
          imported_at: string | null
          imported_by: string | null
          log_id: string
          rows_per_second: number | null
          staging_id: string | null
          success_rows: number | null
          target_table: string | null
          tenant_id: string | null
          total_rows: number | null
        }
        Insert: {
          created_at?: string | null
          duplicate_rows?: number | null
          error_details?: Json | null
          failed_rows?: number | null
          import_duration_ms?: number | null
          import_type?: string | null
          imported_at?: string | null
          imported_by?: string | null
          log_id?: string
          rows_per_second?: number | null
          staging_id?: string | null
          success_rows?: number | null
          target_table?: string | null
          tenant_id?: string | null
          total_rows?: number | null
        }
        Update: {
          created_at?: string | null
          duplicate_rows?: number | null
          error_details?: Json | null
          failed_rows?: number | null
          import_duration_ms?: number | null
          import_type?: string | null
          imported_at?: string | null
          imported_by?: string | null
          log_id?: string
          rows_per_second?: number | null
          staging_id?: string | null
          success_rows?: number | null
          target_table?: string | null
          tenant_id?: string | null
          total_rows?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "data_import_log_staging_id_fkey"
            columns: ["staging_id"]
            isOneToOne: false
            referencedRelation: "raw_data_staging"
            referencedColumns: ["staging_id"]
          },
          {
            foreignKeyName: "data_import_log_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      data_quality_report: {
        Row: {
          accuracy_score: number | null
          completeness_score: number | null
          consistency_score: number | null
          created_at: string | null
          duplicate_count: number | null
          invalid_format_count: number | null
          missing_field_count: number | null
          outlier_count: number | null
          overall_quality_score: number | null
          quality_issues: Json | null
          report_id: string
          staging_id: string | null
          tenant_id: string | null
          validation_rules: Json | null
        }
        Insert: {
          accuracy_score?: number | null
          completeness_score?: number | null
          consistency_score?: number | null
          created_at?: string | null
          duplicate_count?: number | null
          invalid_format_count?: number | null
          missing_field_count?: number | null
          outlier_count?: number | null
          overall_quality_score?: number | null
          quality_issues?: Json | null
          report_id?: string
          staging_id?: string | null
          tenant_id?: string | null
          validation_rules?: Json | null
        }
        Update: {
          accuracy_score?: number | null
          completeness_score?: number | null
          consistency_score?: number | null
          created_at?: string | null
          duplicate_count?: number | null
          invalid_format_count?: number | null
          missing_field_count?: number | null
          outlier_count?: number | null
          overall_quality_score?: number | null
          quality_issues?: Json | null
          report_id?: string
          staging_id?: string | null
          tenant_id?: string | null
          validation_rules?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "data_quality_report_staging_id_fkey"
            columns: ["staging_id"]
            isOneToOne: false
            referencedRelation: "raw_data_staging"
            referencedColumns: ["staging_id"]
          },
          {
            foreignKeyName: "data_quality_report_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      data_version_control: {
        Row: {
          affected_rows: number | null
          change_description: string | null
          change_details: Json | null
          change_type: string | null
          changed_by: string | null
          created_at: string | null
          data_type: string | null
          is_current: boolean | null
          snapshot_file_path: string | null
          tenant_id: string | null
          version_date: string | null
          version_id: string
          version_number: number | null
        }
        Insert: {
          affected_rows?: number | null
          change_description?: string | null
          change_details?: Json | null
          change_type?: string | null
          changed_by?: string | null
          created_at?: string | null
          data_type?: string | null
          is_current?: boolean | null
          snapshot_file_path?: string | null
          tenant_id?: string | null
          version_date?: string | null
          version_id?: string
          version_number?: number | null
        }
        Update: {
          affected_rows?: number | null
          change_description?: string | null
          change_details?: Json | null
          change_type?: string | null
          changed_by?: string | null
          created_at?: string | null
          data_type?: string | null
          is_current?: boolean | null
          snapshot_file_path?: string | null
          tenant_id?: string | null
          version_date?: string | null
          version_id?: string
          version_number?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "data_version_control_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      decision_audit_trail: {
        Row: {
          action_type: string | null
          audit_id: string
          audit_timestamp: string | null
          change_reason: string | null
          changed_by: string | null
          created_at: string | null
          event_id: string | null
          field_changed: string | null
          new_value: string | null
          old_value: string | null
          tenant_id: string | null
        }
        Insert: {
          action_type?: string | null
          audit_id?: string
          audit_timestamp?: string | null
          change_reason?: string | null
          changed_by?: string | null
          created_at?: string | null
          event_id?: string | null
          field_changed?: string | null
          new_value?: string | null
          old_value?: string | null
          tenant_id?: string | null
        }
        Update: {
          action_type?: string | null
          audit_id?: string
          audit_timestamp?: string | null
          change_reason?: string | null
          changed_by?: string | null
          created_at?: string | null
          event_id?: string | null
          field_changed?: string | null
          new_value?: string | null
          old_value?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "decision_audit_trail_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "decision_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "decision_audit_trail_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      decision_cycle_config: {
        Row: {
          created_at: string | null
          created_by: string | null
          cycle_id: string
          cycle_name: string
          cycle_type: string | null
          decision_scope: Json | null
          end_date: string | null
          frequency: string | null
          is_active: boolean | null
          start_date: string | null
          target_metrics: Json | null
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          cycle_id?: string
          cycle_name: string
          cycle_type?: string | null
          decision_scope?: Json | null
          end_date?: string | null
          frequency?: string | null
          is_active?: boolean | null
          start_date?: string | null
          target_metrics?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          cycle_id?: string
          cycle_name?: string
          cycle_type?: string | null
          decision_scope?: Json | null
          end_date?: string | null
          frequency?: string | null
          is_active?: boolean | null
          start_date?: string | null
          target_metrics?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "decision_cycle_config_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      decision_events: {
        Row: {
          approval_status: string | null
          created_at: string | null
          cycle_id: string | null
          decision_description: string | null
          decision_level: string | null
          decision_maker: string | null
          decision_params: Json | null
          department: string | null
          event_category: string | null
          event_date: string
          event_id: string
          event_type: string | null
          expected_benefit: number | null
          expected_cost: number | null
          expected_impact: Json | null
          implementation_status: string | null
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          approval_status?: string | null
          created_at?: string | null
          cycle_id?: string | null
          decision_description?: string | null
          decision_level?: string | null
          decision_maker?: string | null
          decision_params?: Json | null
          department?: string | null
          event_category?: string | null
          event_date: string
          event_id?: string
          event_type?: string | null
          expected_benefit?: number | null
          expected_cost?: number | null
          expected_impact?: Json | null
          implementation_status?: string | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          approval_status?: string | null
          created_at?: string | null
          cycle_id?: string | null
          decision_description?: string | null
          decision_level?: string | null
          decision_maker?: string | null
          decision_params?: Json | null
          department?: string | null
          event_category?: string | null
          event_date?: string
          event_id?: string
          event_type?: string | null
          expected_benefit?: number | null
          expected_cost?: number | null
          expected_impact?: Json | null
          implementation_status?: string | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "decision_events_cycle_id_fkey"
            columns: ["cycle_id"]
            isOneToOne: false
            referencedRelation: "decision_cycle_config"
            referencedColumns: ["cycle_id"]
          },
          {
            foreignKeyName: "decision_events_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      decision_executions: {
        Row: {
          actual_cost: number | null
          budget_variance: number | null
          completion_percentage: number | null
          created_at: string | null
          event_id: string | null
          execution_date: string | null
          execution_details: Json | null
          execution_id: string
          execution_status: string | null
          executor: string | null
          resources_allocated: Json | null
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          actual_cost?: number | null
          budget_variance?: number | null
          completion_percentage?: number | null
          created_at?: string | null
          event_id?: string | null
          execution_date?: string | null
          execution_details?: Json | null
          execution_id?: string
          execution_status?: string | null
          executor?: string | null
          resources_allocated?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          actual_cost?: number | null
          budget_variance?: number | null
          completion_percentage?: number | null
          created_at?: string | null
          event_id?: string | null
          execution_date?: string | null
          execution_details?: Json | null
          execution_id?: string
          execution_status?: string | null
          executor?: string | null
          resources_allocated?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "decision_executions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "decision_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "decision_executions_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      decision_impact_evaluation: {
        Row: {
          actual_benefit: number | null
          actual_impact: Json | null
          attribution_factors: Json | null
          created_at: string | null
          effectiveness_score: number | null
          evaluated_by: string | null
          evaluation_date: string | null
          evaluation_id: string
          evaluation_period: string | null
          event_id: string | null
          expected_vs_actual: Json | null
          external_factors: Json | null
          impact_variance_pct: number | null
          roi: number | null
          tenant_id: string | null
        }
        Insert: {
          actual_benefit?: number | null
          actual_impact?: Json | null
          attribution_factors?: Json | null
          created_at?: string | null
          effectiveness_score?: number | null
          evaluated_by?: string | null
          evaluation_date?: string | null
          evaluation_id?: string
          evaluation_period?: string | null
          event_id?: string | null
          expected_vs_actual?: Json | null
          external_factors?: Json | null
          impact_variance_pct?: number | null
          roi?: number | null
          tenant_id?: string | null
        }
        Update: {
          actual_benefit?: number | null
          actual_impact?: Json | null
          attribution_factors?: Json | null
          created_at?: string | null
          effectiveness_score?: number | null
          evaluated_by?: string | null
          evaluation_date?: string | null
          evaluation_id?: string
          evaluation_period?: string | null
          event_id?: string | null
          expected_vs_actual?: Json | null
          external_factors?: Json | null
          impact_variance_pct?: number | null
          roi?: number | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "decision_impact_evaluation_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "decision_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "decision_impact_evaluation_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_activity: {
        Row: {
          activity_code: string
          activity_id: string
          activity_name: string
          activity_type: string | null
          created_at: string | null
          description: string | null
          tenant_id: string | null
        }
        Insert: {
          activity_code: string
          activity_id?: string
          activity_name: string
          activity_type?: string | null
          created_at?: string | null
          description?: string | null
          tenant_id?: string | null
        }
        Update: {
          activity_code?: string
          activity_id?: string
          activity_name?: string
          activity_type?: string | null
          created_at?: string | null
          description?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_activity_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_business_entity: {
        Row: {
          address: string | null
          contact_person: string | null
          contact_phone: string | null
          created_at: string | null
          entity_code: string
          entity_id: string
          entity_name: string
          entity_type: string | null
          is_active: boolean | null
          legal_name: string | null
          region: string | null
          tax_id: string | null
          tenant_id: string
          updated_at: string | null
        }
        Insert: {
          address?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          entity_code: string
          entity_id?: string
          entity_name: string
          entity_type?: string | null
          is_active?: boolean | null
          legal_name?: string | null
          region?: string | null
          tax_id?: string | null
          tenant_id: string
          updated_at?: string | null
        }
        Update: {
          address?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          entity_code?: string
          entity_id?: string
          entity_name?: string
          entity_type?: string | null
          is_active?: boolean | null
          legal_name?: string | null
          region?: string | null
          tax_id?: string | null
          tenant_id?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      dim_channel: {
        Row: {
          channel_code: string
          channel_id: string
          channel_name: string
          channel_type: string | null
          created_at: string | null
          description: string | null
          tenant_id: string | null
        }
        Insert: {
          channel_code: string
          channel_id?: string
          channel_name: string
          channel_type?: string | null
          created_at?: string | null
          description?: string | null
          tenant_id?: string | null
        }
        Update: {
          channel_code?: string
          channel_id?: string
          channel_name?: string
          channel_type?: string | null
          created_at?: string | null
          description?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_channel_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_conv_channel: {
        Row: {
          channel_code: string
          channel_name: string
          channel_type: string | null
          conv_channel_id: string
          created_at: string | null
          tenant_id: string | null
        }
        Insert: {
          channel_code: string
          channel_name: string
          channel_type?: string | null
          conv_channel_id?: string
          created_at?: string | null
          tenant_id?: string | null
        }
        Update: {
          channel_code?: string
          channel_name?: string
          channel_type?: string | null
          conv_channel_id?: string
          created_at?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_conv_channel_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_customer: {
        Row: {
          created_at: string | null
          customer_code: string
          customer_id: string
          customer_name: string
          customer_segment: string | null
          region: string | null
          tenant_id: string | null
        }
        Insert: {
          created_at?: string | null
          customer_code: string
          customer_id?: string
          customer_name: string
          customer_segment?: string | null
          region?: string | null
          tenant_id?: string | null
        }
        Update: {
          created_at?: string | null
          customer_code?: string
          customer_id?: string
          customer_name?: string
          customer_segment?: string | null
          region?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_customer_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_department: {
        Row: {
          cost_center: string | null
          created_at: string | null
          department_code: string
          department_id: string
          department_level: number | null
          department_name: string
          department_type: string | null
          entity_id: string | null
          is_active: boolean | null
          manager_id: string | null
          parent_department_id: string | null
          tenant_id: string
          updated_at: string | null
        }
        Insert: {
          cost_center?: string | null
          created_at?: string | null
          department_code: string
          department_id?: string
          department_level?: number | null
          department_name: string
          department_type?: string | null
          entity_id?: string | null
          is_active?: boolean | null
          manager_id?: string | null
          parent_department_id?: string | null
          tenant_id: string
          updated_at?: string | null
        }
        Update: {
          cost_center?: string | null
          created_at?: string | null
          department_code?: string
          department_id?: string
          department_level?: number | null
          department_name?: string
          department_type?: string | null
          entity_id?: string | null
          is_active?: boolean | null
          manager_id?: string | null
          parent_department_id?: string | null
          tenant_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_department_parent_department_id_fkey"
            columns: ["parent_department_id"]
            isOneToOne: false
            referencedRelation: "dim_department"
            referencedColumns: ["department_id"]
          },
        ]
      }
      dim_employee: {
        Row: {
          birth_date: string | null
          created_at: string | null
          department_id: string | null
          email: string | null
          employee_code: string
          employee_id: string
          employee_name: string
          employee_name_en: string | null
          employment_type: string | null
          entity_id: string | null
          gender: string | null
          hire_date: string | null
          is_active: boolean | null
          job_level: string | null
          leave_date: string | null
          mobile_phone: string | null
          position: string | null
          status: string | null
          supervisor_id: string | null
          tenant_id: string
          updated_at: string | null
        }
        Insert: {
          birth_date?: string | null
          created_at?: string | null
          department_id?: string | null
          email?: string | null
          employee_code: string
          employee_id?: string
          employee_name: string
          employee_name_en?: string | null
          employment_type?: string | null
          entity_id?: string | null
          gender?: string | null
          hire_date?: string | null
          is_active?: boolean | null
          job_level?: string | null
          leave_date?: string | null
          mobile_phone?: string | null
          position?: string | null
          status?: string | null
          supervisor_id?: string | null
          tenant_id: string
          updated_at?: string | null
        }
        Update: {
          birth_date?: string | null
          created_at?: string | null
          department_id?: string | null
          email?: string | null
          employee_code?: string
          employee_id?: string
          employee_name?: string
          employee_name_en?: string | null
          employment_type?: string | null
          entity_id?: string | null
          gender?: string | null
          hire_date?: string | null
          is_active?: boolean | null
          job_level?: string | null
          leave_date?: string | null
          mobile_phone?: string | null
          position?: string | null
          status?: string | null
          supervisor_id?: string | null
          tenant_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_employee_department_id_fkey"
            columns: ["department_id"]
            isOneToOne: false
            referencedRelation: "dim_department"
            referencedColumns: ["department_id"]
          },
          {
            foreignKeyName: "dim_employee_supervisor_id_fkey"
            columns: ["supervisor_id"]
            isOneToOne: false
            referencedRelation: "dim_employee"
            referencedColumns: ["employee_id"]
          },
        ]
      }
      dim_media_channel: {
        Row: {
          channel_code: string
          channel_name: string
          channel_type: string | null
          cost_per_impression: number | null
          created_at: string | null
          media_channel_id: string
          tenant_id: string | null
        }
        Insert: {
          channel_code: string
          channel_name: string
          channel_type?: string | null
          cost_per_impression?: number | null
          created_at?: string | null
          media_channel_id?: string
          tenant_id?: string | null
        }
        Update: {
          channel_code?: string
          channel_name?: string
          channel_type?: string | null
          cost_per_impression?: number | null
          created_at?: string | null
          media_channel_id?: string
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_media_channel_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_pft: {
        Row: {
          created_at: string | null
          description: string | null
          pft_category: string | null
          pft_code: string
          pft_id: string
          pft_name: string
          tenant_id: string | null
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          pft_category?: string | null
          pft_code: string
          pft_id?: string
          pft_name: string
          tenant_id?: string | null
        }
        Update: {
          created_at?: string | null
          description?: string | null
          pft_category?: string | null
          pft_code?: string
          pft_id?: string
          pft_name?: string
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_pft_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_project: {
        Row: {
          actual_budget: number | null
          created_at: string | null
          department_id: string | null
          description: string | null
          end_date: string | null
          entity_id: string | null
          is_active: boolean | null
          planned_budget: number | null
          priority: string | null
          project_code: string
          project_id: string
          project_manager_id: string | null
          project_name: string
          project_status: string | null
          project_type: string | null
          sponsor_id: string | null
          start_date: string | null
          tenant_id: string
          updated_at: string | null
        }
        Insert: {
          actual_budget?: number | null
          created_at?: string | null
          department_id?: string | null
          description?: string | null
          end_date?: string | null
          entity_id?: string | null
          is_active?: boolean | null
          planned_budget?: number | null
          priority?: string | null
          project_code: string
          project_id?: string
          project_manager_id?: string | null
          project_name: string
          project_status?: string | null
          project_type?: string | null
          sponsor_id?: string | null
          start_date?: string | null
          tenant_id: string
          updated_at?: string | null
        }
        Update: {
          actual_budget?: number | null
          created_at?: string | null
          department_id?: string | null
          description?: string | null
          end_date?: string | null
          entity_id?: string | null
          is_active?: boolean | null
          planned_budget?: number | null
          priority?: string | null
          project_code?: string
          project_id?: string
          project_manager_id?: string | null
          project_name?: string
          project_status?: string | null
          project_type?: string | null
          sponsor_id?: string | null
          start_date?: string | null
          tenant_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_project_department_id_fkey"
            columns: ["department_id"]
            isOneToOne: false
            referencedRelation: "dim_department"
            referencedColumns: ["department_id"]
          },
          {
            foreignKeyName: "dim_project_project_manager_id_fkey"
            columns: ["project_manager_id"]
            isOneToOne: false
            referencedRelation: "dim_employee"
            referencedColumns: ["employee_id"]
          },
        ]
      }
      dim_sku: {
        Row: {
          category: string | null
          created_at: string | null
          sku_code: string
          sku_id: string
          sku_name: string
          tenant_id: string | null
          unit_price: number | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          sku_code: string
          sku_id?: string
          sku_name: string
          tenant_id?: string | null
          unit_price?: number | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          sku_code?: string
          sku_id?: string
          sku_name?: string
          tenant_id?: string | null
          unit_price?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_sku_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_supplier: {
        Row: {
          created_at: string | null
          rating: number | null
          region: string | null
          supplier_code: string
          supplier_id: string
          supplier_name: string
          tenant_id: string | null
        }
        Insert: {
          created_at?: string | null
          rating?: number | null
          region?: string | null
          supplier_code: string
          supplier_id?: string
          supplier_name: string
          tenant_id?: string | null
        }
        Update: {
          created_at?: string | null
          rating?: number | null
          region?: string | null
          supplier_code?: string
          supplier_id?: string
          supplier_name?: string
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dim_supplier_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      dim_vpt: {
        Row: {
          created_at: string | null
          description: string | null
          tenant_id: string | null
          vpt_category: string | null
          vpt_code: string
          vpt_id: string
          vpt_name: string
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          tenant_id?: string | null
          vpt_category?: string | null
          vpt_code: string
          vpt_id?: string
          vpt_name: string
        }
        Update: {
          created_at?: string | null
          description?: string | null
          tenant_id?: string | null
          vpt_category?: string | null
          vpt_code?: string
          vpt_id?: string
          vpt_name?: string
        }
        Relationships: [
          {
            foreignKeyName: "dim_vpt_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      document_relation: {
        Row: {
          created_at: string | null
          related_quantity: number | null
          relation_id: string
          relation_type: string | null
          source_doc_id: string
          source_doc_line_id: string | null
          source_doc_type: string
          target_doc_id: string
          target_doc_line_id: string | null
          target_doc_type: string
          tenant_id: string | null
        }
        Insert: {
          created_at?: string | null
          related_quantity?: number | null
          relation_id?: string
          relation_type?: string | null
          source_doc_id: string
          source_doc_line_id?: string | null
          source_doc_type: string
          target_doc_id: string
          target_doc_line_id?: string | null
          target_doc_type: string
          tenant_id?: string | null
        }
        Update: {
          created_at?: string | null
          related_quantity?: number | null
          relation_id?: string
          relation_type?: string | null
          source_doc_id?: string
          source_doc_line_id?: string | null
          source_doc_type?: string
          target_doc_id?: string
          target_doc_line_id?: string | null
          target_doc_type?: string
          tenant_id?: string | null
        }
        Relationships: []
      }
      external_business_facts: {
        Row: {
          created_at: string | null
          data_source: string | null
          fact_category: string | null
          fact_id: string
          fact_name: string
          fact_source: string | null
          fact_unit: string | null
          fact_value: number | null
          impact_on_business: string | null
          observation_date: string | null
          relevance_score: number | null
          tenant_id: string | null
          trend_confidence: number | null
          trend_direction: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          data_source?: string | null
          fact_category?: string | null
          fact_id?: string
          fact_name: string
          fact_source?: string | null
          fact_unit?: string | null
          fact_value?: number | null
          impact_on_business?: string | null
          observation_date?: string | null
          relevance_score?: number | null
          tenant_id?: string | null
          trend_confidence?: number | null
          trend_direction?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          data_source?: string | null
          fact_category?: string | null
          fact_id?: string
          fact_name?: string
          fact_source?: string | null
          fact_unit?: string | null
          fact_value?: number | null
          impact_on_business?: string | null
          observation_date?: string | null
          relevance_score?: number | null
          tenant_id?: string | null
          trend_confidence?: number | null
          trend_direction?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "external_business_facts_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      fact_expense: {
        Row: {
          activity_id: string | null
          created_at: string | null
          expense_amount: number
          expense_date: string
          expense_id: string
          expense_type: string | null
          tenant_id: string | null
        }
        Insert: {
          activity_id?: string | null
          created_at?: string | null
          expense_amount: number
          expense_date: string
          expense_id?: string
          expense_type?: string | null
          tenant_id?: string | null
        }
        Update: {
          activity_id?: string | null
          created_at?: string | null
          expense_amount?: number
          expense_date?: string
          expense_id?: string
          expense_type?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fact_expense_activity_id_fkey"
            columns: ["activity_id"]
            isOneToOne: false
            referencedRelation: "dim_activity"
            referencedColumns: ["activity_id"]
          },
          {
            foreignKeyName: "fact_expense_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      fact_order: {
        Row: {
          channel_id: string | null
          created_at: string | null
          customer_id: string | null
          order_amount: number
          order_date: string
          order_id: string
          quantity: number
          sku_id: string | null
          tenant_id: string | null
        }
        Insert: {
          channel_id?: string | null
          created_at?: string | null
          customer_id?: string | null
          order_amount: number
          order_date: string
          order_id?: string
          quantity: number
          sku_id?: string | null
          tenant_id?: string | null
        }
        Update: {
          channel_id?: string | null
          created_at?: string | null
          customer_id?: string | null
          order_amount?: number
          order_date?: string
          order_id?: string
          quantity?: number
          sku_id?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fact_order_channel_id_fkey"
            columns: ["channel_id"]
            isOneToOne: false
            referencedRelation: "dim_channel"
            referencedColumns: ["channel_id"]
          },
          {
            foreignKeyName: "fact_order_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "dim_customer"
            referencedColumns: ["customer_id"]
          },
          {
            foreignKeyName: "fact_order_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "fact_order_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      fact_produce: {
        Row: {
          cost: number | null
          created_at: string | null
          produce_date: string
          produce_id: string
          quantity: number
          sku_id: string | null
          tenant_id: string | null
        }
        Insert: {
          cost?: number | null
          created_at?: string | null
          produce_date: string
          produce_id?: string
          quantity: number
          sku_id?: string | null
          tenant_id?: string | null
        }
        Update: {
          cost?: number | null
          created_at?: string | null
          produce_date?: string
          produce_id?: string
          quantity?: number
          sku_id?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fact_produce_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "fact_produce_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      fact_supplier: {
        Row: {
          created_at: string | null
          sku_id: string | null
          supplier_fact_id: string
          supplier_id: string | null
          supply_amount: number | null
          supply_date: string
          tenant_id: string | null
        }
        Insert: {
          created_at?: string | null
          sku_id?: string | null
          supplier_fact_id?: string
          supplier_id?: string | null
          supply_amount?: number | null
          supply_date: string
          tenant_id?: string | null
        }
        Update: {
          created_at?: string | null
          sku_id?: string | null
          supplier_fact_id?: string
          supplier_id?: string | null
          supply_amount?: number | null
          supply_date?: string
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fact_supplier_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "fact_supplier_supplier_id_fkey"
            columns: ["supplier_id"]
            isOneToOne: false
            referencedRelation: "dim_supplier"
            referencedColumns: ["supplier_id"]
          },
          {
            foreignKeyName: "fact_supplier_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      fact_voice: {
        Row: {
          created_at: string | null
          customer_id: string | null
          satisfaction_score: number | null
          sentiment: string | null
          sku_id: string | null
          tenant_id: string | null
          voice_content: string | null
          voice_date: string
          voice_id: string
        }
        Insert: {
          created_at?: string | null
          customer_id?: string | null
          satisfaction_score?: number | null
          sentiment?: string | null
          sku_id?: string | null
          tenant_id?: string | null
          voice_content?: string | null
          voice_date: string
          voice_id?: string
        }
        Update: {
          created_at?: string | null
          customer_id?: string | null
          satisfaction_score?: number | null
          sentiment?: string | null
          sku_id?: string | null
          tenant_id?: string | null
          voice_content?: string | null
          voice_date?: string
          voice_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "fact_voice_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "dim_customer"
            referencedColumns: ["customer_id"]
          },
          {
            foreignKeyName: "fact_voice_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "fact_voice_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      manager_evaluation: {
        Row: {
          avg_implementation_time: number | null
          budget_adherence_pct: number | null
          created_at: string | null
          decision_count: number | null
          decision_quality_score: number | null
          department: string | null
          evaluated_by: string | null
          evaluation_date: string | null
          evaluation_id: string
          evaluation_period_end: string | null
          evaluation_period_start: string | null
          execution_efficiency_score: number | null
          impact_score: number | null
          improvement_areas: string | null
          manager_id: string | null
          manager_level: string | null
          overall_score: number | null
          performance_level: string | null
          recommendations: string | null
          roi_achieved: number | null
          strengths: string | null
          successful_decisions: number | null
          tenant_id: string | null
        }
        Insert: {
          avg_implementation_time?: number | null
          budget_adherence_pct?: number | null
          created_at?: string | null
          decision_count?: number | null
          decision_quality_score?: number | null
          department?: string | null
          evaluated_by?: string | null
          evaluation_date?: string | null
          evaluation_id?: string
          evaluation_period_end?: string | null
          evaluation_period_start?: string | null
          execution_efficiency_score?: number | null
          impact_score?: number | null
          improvement_areas?: string | null
          manager_id?: string | null
          manager_level?: string | null
          overall_score?: number | null
          performance_level?: string | null
          recommendations?: string | null
          roi_achieved?: number | null
          strengths?: string | null
          successful_decisions?: number | null
          tenant_id?: string | null
        }
        Update: {
          avg_implementation_time?: number | null
          budget_adherence_pct?: number | null
          created_at?: string | null
          decision_count?: number | null
          decision_quality_score?: number | null
          department?: string | null
          evaluated_by?: string | null
          evaluation_date?: string | null
          evaluation_id?: string
          evaluation_period_end?: string | null
          evaluation_period_start?: string | null
          execution_efficiency_score?: number | null
          impact_score?: number | null
          improvement_areas?: string | null
          manager_id?: string | null
          manager_level?: string | null
          overall_score?: number | null
          performance_level?: string | null
          recommendations?: string | null
          roi_achieved?: number | null
          strengths?: string | null
          successful_decisions?: number | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "manager_evaluation_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      marginal_dynamic_weights: {
        Row: {
          created_at: string | null
          effective_date: string | null
          factor_name: string | null
          factor_type: string | null
          initial_weight: number | null
          learned_weight: number | null
          tenant_id: string | null
          time_decay_factor: number | null
          training_id: string | null
          weight_change_pct: number | null
          weight_confidence: number | null
          weight_id: string
        }
        Insert: {
          created_at?: string | null
          effective_date?: string | null
          factor_name?: string | null
          factor_type?: string | null
          initial_weight?: number | null
          learned_weight?: number | null
          tenant_id?: string | null
          time_decay_factor?: number | null
          training_id?: string | null
          weight_change_pct?: number | null
          weight_confidence?: number | null
          weight_id?: string
        }
        Update: {
          created_at?: string | null
          effective_date?: string | null
          factor_name?: string | null
          factor_type?: string | null
          initial_weight?: number | null
          learned_weight?: number | null
          tenant_id?: string | null
          time_decay_factor?: number | null
          training_id?: string | null
          weight_change_pct?: number | null
          weight_confidence?: number | null
          weight_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "marginal_dynamic_weights_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_dynamic_weights_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_ensemble_models: {
        Row: {
          best_single_model_r_squared: number | null
          created_at: string | null
          created_by: string | null
          ensemble_id: string
          ensemble_mae: number | null
          ensemble_name: string | null
          ensemble_r_squared: number | null
          ensemble_rmse: number | null
          ensemble_type: string | null
          improvement_over_best: number | null
          is_active: boolean | null
          member_models: Json | null
          model_weights: Json | null
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          best_single_model_r_squared?: number | null
          created_at?: string | null
          created_by?: string | null
          ensemble_id?: string
          ensemble_mae?: number | null
          ensemble_name?: string | null
          ensemble_r_squared?: number | null
          ensemble_rmse?: number | null
          ensemble_type?: string | null
          improvement_over_best?: number | null
          is_active?: boolean | null
          member_models?: Json | null
          model_weights?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          best_single_model_r_squared?: number | null
          created_at?: string | null
          created_by?: string | null
          ensemble_id?: string
          ensemble_mae?: number | null
          ensemble_name?: string | null
          ensemble_r_squared?: number | null
          ensemble_rmse?: number | null
          ensemble_type?: string | null
          improvement_over_best?: number | null
          is_active?: boolean | null
          member_models?: Json | null
          model_weights?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_ensemble_models_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      marginal_fitting_config: {
        Row: {
          algorithm_params: Json | null
          analysis_type: string | null
          confidence_level: number | null
          config_id: string
          config_name: string
          created_at: string | null
          created_by: string | null
          fitting_method: string | null
          is_active: boolean | null
          min_data_points: number | null
          tenant_id: string | null
          time_window_months: number | null
          updated_at: string | null
        }
        Insert: {
          algorithm_params?: Json | null
          analysis_type?: string | null
          confidence_level?: number | null
          config_id?: string
          config_name: string
          created_at?: string | null
          created_by?: string | null
          fitting_method?: string | null
          is_active?: boolean | null
          min_data_points?: number | null
          tenant_id?: string | null
          time_window_months?: number | null
          updated_at?: string | null
        }
        Update: {
          algorithm_params?: Json | null
          analysis_type?: string | null
          confidence_level?: number | null
          config_id?: string
          config_name?: string
          created_at?: string | null
          created_by?: string | null
          fitting_method?: string | null
          is_active?: boolean | null
          min_data_points?: number | null
          tenant_id?: string | null
          time_window_months?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_fitting_config_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      marginal_impact_analysis: {
        Row: {
          analysis_date: string | null
          analysis_id: string
          baseline_value: number | null
          confidence_lower: number | null
          confidence_upper: number | null
          created_at: string | null
          elasticity: number | null
          input_variable: string | null
          is_significant: boolean | null
          marginal_impact: number | null
          p_value: number | null
          target_metric: string | null
          tenant_id: string | null
          training_id: string | null
        }
        Insert: {
          analysis_date?: string | null
          analysis_id?: string
          baseline_value?: number | null
          confidence_lower?: number | null
          confidence_upper?: number | null
          created_at?: string | null
          elasticity?: number | null
          input_variable?: string | null
          is_significant?: boolean | null
          marginal_impact?: number | null
          p_value?: number | null
          target_metric?: string | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Update: {
          analysis_date?: string | null
          analysis_id?: string
          baseline_value?: number | null
          confidence_lower?: number | null
          confidence_upper?: number | null
          created_at?: string | null
          elasticity?: number | null
          input_variable?: string | null
          is_significant?: boolean | null
          marginal_impact?: number | null
          p_value?: number | null
          target_metric?: string | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_impact_analysis_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_impact_analysis_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_lag_analysis: {
        Row: {
          analysis_date: string | null
          correlation: number | null
          created_at: string | null
          cumulative_impact: number | null
          is_significant: boolean | null
          lag_id: string
          lag_period: number | null
          lag_unit: string | null
          lagged_impact: number | null
          p_value: number | null
          tenant_id: string | null
          training_id: string | null
          variable_name: string | null
        }
        Insert: {
          analysis_date?: string | null
          correlation?: number | null
          created_at?: string | null
          cumulative_impact?: number | null
          is_significant?: boolean | null
          lag_id?: string
          lag_period?: number | null
          lag_unit?: string | null
          lagged_impact?: number | null
          p_value?: number | null
          tenant_id?: string | null
          training_id?: string | null
          variable_name?: string | null
        }
        Update: {
          analysis_date?: string | null
          correlation?: number | null
          created_at?: string | null
          cumulative_impact?: number | null
          is_significant?: boolean | null
          lag_id?: string
          lag_period?: number | null
          lag_unit?: string | null
          lagged_impact?: number | null
          p_value?: number | null
          tenant_id?: string | null
          training_id?: string | null
          variable_name?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_lag_analysis_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_lag_analysis_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_model_performance: {
        Row: {
          created_at: string | null
          current_mae: number | null
          current_mape: number | null
          current_r_squared: number | null
          current_rmse: number | null
          drift_detected: boolean | null
          mae_change: number | null
          monitoring_date: string | null
          monitoring_period: string | null
          performance_id: string
          performance_status: string | null
          prediction_accuracy: number | null
          prediction_bias: number | null
          r_squared_change: number | null
          requires_retraining: boolean | null
          stability_score: number | null
          tenant_id: string | null
          training_id: string | null
        }
        Insert: {
          created_at?: string | null
          current_mae?: number | null
          current_mape?: number | null
          current_r_squared?: number | null
          current_rmse?: number | null
          drift_detected?: boolean | null
          mae_change?: number | null
          monitoring_date?: string | null
          monitoring_period?: string | null
          performance_id?: string
          performance_status?: string | null
          prediction_accuracy?: number | null
          prediction_bias?: number | null
          r_squared_change?: number | null
          requires_retraining?: boolean | null
          stability_score?: number | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Update: {
          created_at?: string | null
          current_mae?: number | null
          current_mape?: number | null
          current_r_squared?: number | null
          current_rmse?: number | null
          drift_detected?: boolean | null
          mae_change?: number | null
          monitoring_date?: string | null
          monitoring_period?: string | null
          performance_id?: string
          performance_status?: string | null
          prediction_accuracy?: number | null
          prediction_bias?: number | null
          r_squared_change?: number | null
          requires_retraining?: boolean | null
          stability_score?: number | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_model_performance_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_model_performance_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_model_training: {
        Row: {
          config_id: string | null
          created_at: string | null
          feature_importance: Json | null
          mae: number | null
          mape: number | null
          model_params: Json | null
          model_type: string | null
          model_version: string | null
          r_squared: number | null
          rmse: number | null
          tenant_id: string | null
          trained_by: string | null
          training_data_end_date: string | null
          training_data_start_date: string | null
          training_date: string | null
          training_duration_ms: number | null
          training_id: string
          training_samples: number | null
          training_status: string | null
          validation_samples: number | null
        }
        Insert: {
          config_id?: string | null
          created_at?: string | null
          feature_importance?: Json | null
          mae?: number | null
          mape?: number | null
          model_params?: Json | null
          model_type?: string | null
          model_version?: string | null
          r_squared?: number | null
          rmse?: number | null
          tenant_id?: string | null
          trained_by?: string | null
          training_data_end_date?: string | null
          training_data_start_date?: string | null
          training_date?: string | null
          training_duration_ms?: number | null
          training_id?: string
          training_samples?: number | null
          training_status?: string | null
          validation_samples?: number | null
        }
        Update: {
          config_id?: string | null
          created_at?: string | null
          feature_importance?: Json | null
          mae?: number | null
          mape?: number | null
          model_params?: Json | null
          model_type?: string | null
          model_version?: string | null
          r_squared?: number | null
          rmse?: number | null
          tenant_id?: string | null
          trained_by?: string | null
          training_data_end_date?: string | null
          training_data_start_date?: string | null
          training_date?: string | null
          training_duration_ms?: number | null
          training_id?: string
          training_samples?: number | null
          training_status?: string | null
          validation_samples?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_model_training_config_id_fkey"
            columns: ["config_id"]
            isOneToOne: false
            referencedRelation: "marginal_fitting_config"
            referencedColumns: ["config_id"]
          },
          {
            foreignKeyName: "marginal_model_training_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      marginal_optimization_recommendations: {
        Row: {
          action_variables: Json | null
          analysis_id: string | null
          confidence_level: number | null
          created_at: string | null
          current_value: number | null
          estimated_cost: number | null
          expected_impact: number | null
          generated_date: string | null
          implementation_status: string | null
          improvement_pct: number | null
          priority_level: string | null
          recommendation_id: string
          recommendation_type: string | null
          recommended_action: string | null
          roi_estimate: number | null
          target_metric: string | null
          target_value: number | null
          tenant_id: string | null
        }
        Insert: {
          action_variables?: Json | null
          analysis_id?: string | null
          confidence_level?: number | null
          created_at?: string | null
          current_value?: number | null
          estimated_cost?: number | null
          expected_impact?: number | null
          generated_date?: string | null
          implementation_status?: string | null
          improvement_pct?: number | null
          priority_level?: string | null
          recommendation_id?: string
          recommendation_type?: string | null
          recommended_action?: string | null
          roi_estimate?: number | null
          target_metric?: string | null
          target_value?: number | null
          tenant_id?: string | null
        }
        Update: {
          action_variables?: Json | null
          analysis_id?: string | null
          confidence_level?: number | null
          created_at?: string | null
          current_value?: number | null
          estimated_cost?: number | null
          expected_impact?: number | null
          generated_date?: string | null
          implementation_status?: string | null
          improvement_pct?: number | null
          priority_level?: string | null
          recommendation_id?: string
          recommendation_type?: string | null
          recommended_action?: string | null
          roi_estimate?: number | null
          target_metric?: string | null
          target_value?: number | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_optimization_recommendations_analysis_id_fkey"
            columns: ["analysis_id"]
            isOneToOne: false
            referencedRelation: "marginal_impact_analysis"
            referencedColumns: ["analysis_id"]
          },
          {
            foreignKeyName: "marginal_optimization_recommendations_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      marginal_predictions: {
        Row: {
          actual_value: number | null
          confidence_level: number | null
          created_at: string | null
          predicted_value: number | null
          prediction_date: string | null
          prediction_error: number | null
          prediction_horizon: number | null
          prediction_id: string
          prediction_lower: number | null
          prediction_upper: number | null
          target_metric: string | null
          tenant_id: string | null
          training_id: string | null
        }
        Insert: {
          actual_value?: number | null
          confidence_level?: number | null
          created_at?: string | null
          predicted_value?: number | null
          prediction_date?: string | null
          prediction_error?: number | null
          prediction_horizon?: number | null
          prediction_id?: string
          prediction_lower?: number | null
          prediction_upper?: number | null
          target_metric?: string | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Update: {
          actual_value?: number | null
          confidence_level?: number | null
          created_at?: string | null
          predicted_value?: number | null
          prediction_date?: string | null
          prediction_error?: number | null
          prediction_horizon?: number | null
          prediction_id?: string
          prediction_lower?: number | null
          prediction_upper?: number | null
          target_metric?: string | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_predictions_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_predictions_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_synergy_analysis: {
        Row: {
          analysis_date: string | null
          combined_impact: number | null
          created_at: string | null
          factor_a: string | null
          factor_a_impact: number | null
          factor_b: string | null
          factor_b_impact: number | null
          is_significant: boolean | null
          p_value: number | null
          synergy_id: string
          synergy_type: string | null
          synergy_value: number | null
          tenant_id: string | null
          training_id: string | null
        }
        Insert: {
          analysis_date?: string | null
          combined_impact?: number | null
          created_at?: string | null
          factor_a?: string | null
          factor_a_impact?: number | null
          factor_b?: string | null
          factor_b_impact?: number | null
          is_significant?: boolean | null
          p_value?: number | null
          synergy_id?: string
          synergy_type?: string | null
          synergy_value?: number | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Update: {
          analysis_date?: string | null
          combined_impact?: number | null
          created_at?: string | null
          factor_a?: string | null
          factor_a_impact?: number | null
          factor_b?: string | null
          factor_b_impact?: number | null
          is_significant?: boolean | null
          p_value?: number | null
          synergy_id?: string
          synergy_type?: string | null
          synergy_value?: number | null
          tenant_id?: string | null
          training_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_synergy_analysis_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_synergy_analysis_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_threshold_analysis: {
        Row: {
          created_at: string | null
          identified_date: string | null
          impact_after_threshold: number | null
          impact_before_threshold: number | null
          impact_change: number | null
          tenant_id: string | null
          threshold_confidence: number | null
          threshold_id: string
          threshold_type: string | null
          threshold_value: number | null
          training_id: string | null
          variable_name: string | null
        }
        Insert: {
          created_at?: string | null
          identified_date?: string | null
          impact_after_threshold?: number | null
          impact_before_threshold?: number | null
          impact_change?: number | null
          tenant_id?: string | null
          threshold_confidence?: number | null
          threshold_id?: string
          threshold_type?: string | null
          threshold_value?: number | null
          training_id?: string | null
          variable_name?: string | null
        }
        Update: {
          created_at?: string | null
          identified_date?: string | null
          impact_after_threshold?: number | null
          impact_before_threshold?: number | null
          impact_change?: number | null
          tenant_id?: string | null
          threshold_confidence?: number | null
          threshold_id?: string
          threshold_type?: string | null
          threshold_value?: number | null
          training_id?: string | null
          variable_name?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_threshold_analysis_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_threshold_analysis_training_id_fkey"
            columns: ["training_id"]
            isOneToOne: false
            referencedRelation: "marginal_model_training"
            referencedColumns: ["training_id"]
          },
        ]
      }
      marginal_weight_validation: {
        Row: {
          actual_weight: number | null
          adjustment_needed: boolean | null
          created_at: string | null
          deviation_pct: number | null
          expected_weight: number | null
          is_significant: boolean | null
          is_valid: boolean | null
          p_value: number | null
          recommended_weight: number | null
          tenant_id: string | null
          validated_by: string | null
          validation_date: string | null
          validation_id: string
          validation_method: string | null
          validation_score: number | null
          weight_id: string | null
        }
        Insert: {
          actual_weight?: number | null
          adjustment_needed?: boolean | null
          created_at?: string | null
          deviation_pct?: number | null
          expected_weight?: number | null
          is_significant?: boolean | null
          is_valid?: boolean | null
          p_value?: number | null
          recommended_weight?: number | null
          tenant_id?: string | null
          validated_by?: string | null
          validation_date?: string | null
          validation_id?: string
          validation_method?: string | null
          validation_score?: number | null
          weight_id?: string | null
        }
        Update: {
          actual_weight?: number | null
          adjustment_needed?: boolean | null
          created_at?: string | null
          deviation_pct?: number | null
          expected_weight?: number | null
          is_significant?: boolean | null
          is_valid?: boolean | null
          p_value?: number | null
          recommended_weight?: number | null
          tenant_id?: string | null
          validated_by?: string | null
          validation_date?: string | null
          validation_id?: string
          validation_method?: string | null
          validation_score?: number | null
          weight_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "marginal_weight_validation_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
          {
            foreignKeyName: "marginal_weight_validation_weight_id_fkey"
            columns: ["weight_id"]
            isOneToOne: false
            referencedRelation: "marginal_dynamic_weights"
            referencedColumns: ["weight_id"]
          },
        ]
      }
      periodic_report_config: {
        Row: {
          analysis_dimensions: Json | null
          config_id: string
          created_at: string | null
          created_by: string | null
          frequency: string | null
          included_metrics: Json | null
          is_active: boolean | null
          last_generated_at: string | null
          recipients: Json | null
          report_name: string
          report_type: string | null
          schedule_config: Json | null
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          analysis_dimensions?: Json | null
          config_id?: string
          created_at?: string | null
          created_by?: string | null
          frequency?: string | null
          included_metrics?: Json | null
          is_active?: boolean | null
          last_generated_at?: string | null
          recipients?: Json | null
          report_name: string
          report_type?: string | null
          schedule_config?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          analysis_dimensions?: Json | null
          config_id?: string
          created_at?: string | null
          created_by?: string | null
          frequency?: string | null
          included_metrics?: Json | null
          is_active?: boolean | null
          last_generated_at?: string | null
          recipients?: Json | null
          report_name?: string
          report_type?: string | null
          schedule_config?: Json | null
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "periodic_report_config_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      purchase_invoice_header: {
        Row: {
          created_at: string | null
          created_by: string | null
          currency_code: string | null
          discount_amount: number | null
          due_date: string | null
          invoice_date: string
          invoice_id: string
          invoice_number: string
          invoice_status: string | null
          invoice_type: string | null
          net_amount: number | null
          paid_amount: number | null
          payment_status: string | null
          payment_term: string | null
          remark: string | null
          supplier_id: string | null
          tax_amount: number | null
          tenant_id: string | null
          total_amount: number | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          discount_amount?: number | null
          due_date?: string | null
          invoice_date: string
          invoice_id?: string
          invoice_number: string
          invoice_status?: string | null
          invoice_type?: string | null
          net_amount?: number | null
          paid_amount?: number | null
          payment_status?: string | null
          payment_term?: string | null
          remark?: string | null
          supplier_id?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          discount_amount?: number | null
          due_date?: string | null
          invoice_date?: string
          invoice_id?: string
          invoice_number?: string
          invoice_status?: string | null
          invoice_type?: string | null
          net_amount?: number | null
          paid_amount?: number | null
          payment_status?: string | null
          payment_term?: string | null
          remark?: string | null
          supplier_id?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "purchase_invoice_header_supplier_id_fkey"
            columns: ["supplier_id"]
            isOneToOne: false
            referencedRelation: "dim_supplier"
            referencedColumns: ["supplier_id"]
          },
        ]
      }
      purchase_invoice_line: {
        Row: {
          created_at: string | null
          discount_amount: number | null
          invoice_id: string
          line_amount: number
          line_id: string
          line_number: number
          net_amount: number
          quantity: number
          remark: string | null
          sku_code: string | null
          sku_id: string | null
          sku_name: string | null
          source_po_id: string | null
          source_po_line_id: string | null
          source_receipt_id: string | null
          source_receipt_line_id: string | null
          tax_amount: number | null
          tax_rate: number | null
          tenant_id: string | null
          unit_price: number
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          discount_amount?: number | null
          invoice_id: string
          line_amount: number
          line_id?: string
          line_number: number
          net_amount: number
          quantity: number
          remark?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_po_id?: string | null
          source_po_line_id?: string | null
          source_receipt_id?: string | null
          source_receipt_line_id?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price: number
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          discount_amount?: number | null
          invoice_id?: string
          line_amount?: number
          line_id?: string
          line_number?: number
          net_amount?: number
          quantity?: number
          remark?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_po_id?: string | null
          source_po_line_id?: string | null
          source_receipt_id?: string | null
          source_receipt_line_id?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price?: number
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "purchase_invoice_line_invoice_id_fkey"
            columns: ["invoice_id"]
            isOneToOne: false
            referencedRelation: "purchase_invoice_header"
            referencedColumns: ["invoice_id"]
          },
          {
            foreignKeyName: "purchase_invoice_line_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "purchase_invoice_line_source_po_id_fkey"
            columns: ["source_po_id"]
            isOneToOne: false
            referencedRelation: "purchase_order_header"
            referencedColumns: ["po_id"]
          },
          {
            foreignKeyName: "purchase_invoice_line_source_po_line_id_fkey"
            columns: ["source_po_line_id"]
            isOneToOne: false
            referencedRelation: "purchase_order_line"
            referencedColumns: ["line_id"]
          },
          {
            foreignKeyName: "purchase_invoice_line_source_receipt_id_fkey"
            columns: ["source_receipt_id"]
            isOneToOne: false
            referencedRelation: "receipt_header"
            referencedColumns: ["receipt_id"]
          },
          {
            foreignKeyName: "purchase_invoice_line_source_receipt_line_id_fkey"
            columns: ["source_receipt_line_id"]
            isOneToOne: false
            referencedRelation: "receipt_line"
            referencedColumns: ["line_id"]
          },
        ]
      }
      purchase_order_header: {
        Row: {
          approved_at: string | null
          approved_by: string | null
          contact_person: string | null
          contact_phone: string | null
          created_at: string | null
          created_by: string | null
          currency_code: string | null
          delivery_address: string | null
          discount_amount: number | null
          net_amount: number | null
          payment_term: string | null
          po_date: string
          po_id: string
          po_number: string
          po_status: string | null
          remark: string | null
          supplier_id: string | null
          tax_amount: number | null
          tenant_id: string | null
          total_amount: number | null
          updated_at: string | null
        }
        Insert: {
          approved_at?: string | null
          approved_by?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          delivery_address?: string | null
          discount_amount?: number | null
          net_amount?: number | null
          payment_term?: string | null
          po_date: string
          po_id?: string
          po_number: string
          po_status?: string | null
          remark?: string | null
          supplier_id?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Update: {
          approved_at?: string | null
          approved_by?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          delivery_address?: string | null
          discount_amount?: number | null
          net_amount?: number | null
          payment_term?: string | null
          po_date?: string
          po_id?: string
          po_number?: string
          po_status?: string | null
          remark?: string | null
          supplier_id?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "purchase_order_header_supplier_id_fkey"
            columns: ["supplier_id"]
            isOneToOne: false
            referencedRelation: "dim_supplier"
            referencedColumns: ["supplier_id"]
          },
        ]
      }
      purchase_order_line: {
        Row: {
          created_at: string | null
          discount_amount: number | null
          invoiced_quantity: number | null
          line_amount: number
          line_id: string
          line_number: number
          line_status: string | null
          net_amount: number
          po_id: string
          promised_delivery_date: string | null
          quantity: number
          received_quantity: number | null
          remark: string | null
          requested_delivery_date: string | null
          sku_code: string | null
          sku_id: string | null
          sku_name: string | null
          tax_amount: number | null
          tax_rate: number | null
          tenant_id: string | null
          unit_price: number
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          discount_amount?: number | null
          invoiced_quantity?: number | null
          line_amount: number
          line_id?: string
          line_number: number
          line_status?: string | null
          net_amount: number
          po_id: string
          promised_delivery_date?: string | null
          quantity: number
          received_quantity?: number | null
          remark?: string | null
          requested_delivery_date?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price: number
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          discount_amount?: number | null
          invoiced_quantity?: number | null
          line_amount?: number
          line_id?: string
          line_number?: number
          line_status?: string | null
          net_amount?: number
          po_id?: string
          promised_delivery_date?: string | null
          quantity?: number
          received_quantity?: number | null
          remark?: string | null
          requested_delivery_date?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price?: number
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "purchase_order_line_po_id_fkey"
            columns: ["po_id"]
            isOneToOne: false
            referencedRelation: "purchase_order_header"
            referencedColumns: ["po_id"]
          },
          {
            foreignKeyName: "purchase_order_line_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
        ]
      }
      raw_data_staging: {
        Row: {
          column_count: number | null
          created_at: string | null
          detected_format: string | null
          document_type: string | null
          error_message: string | null
          failed_row_count: number | null
          file_name: string
          file_size_kb: number | null
          file_type: string | null
          format_characteristics: Json | null
          format_confidence: number | null
          processed_at: string | null
          processed_row_count: number | null
          processing_duration_ms: number | null
          quality_score: number | null
          raw_data: Json | null
          row_count: number | null
          staging_id: string
          tenant_id: string | null
          upload_status: string | null
          uploaded_at: string | null
          uploaded_by: string | null
        }
        Insert: {
          column_count?: number | null
          created_at?: string | null
          detected_format?: string | null
          document_type?: string | null
          error_message?: string | null
          failed_row_count?: number | null
          file_name: string
          file_size_kb?: number | null
          file_type?: string | null
          format_characteristics?: Json | null
          format_confidence?: number | null
          processed_at?: string | null
          processed_row_count?: number | null
          processing_duration_ms?: number | null
          quality_score?: number | null
          raw_data?: Json | null
          row_count?: number | null
          staging_id?: string
          tenant_id?: string | null
          upload_status?: string | null
          uploaded_at?: string | null
          uploaded_by?: string | null
        }
        Update: {
          column_count?: number | null
          created_at?: string | null
          detected_format?: string | null
          document_type?: string | null
          error_message?: string | null
          failed_row_count?: number | null
          file_name?: string
          file_size_kb?: number | null
          file_type?: string | null
          format_characteristics?: Json | null
          format_confidence?: number | null
          processed_at?: string | null
          processed_row_count?: number | null
          processing_duration_ms?: number | null
          quality_score?: number | null
          raw_data?: Json | null
          row_count?: number | null
          staging_id?: string
          tenant_id?: string | null
          upload_status?: string | null
          uploaded_at?: string | null
          uploaded_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "raw_data_staging_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      receipt_header: {
        Row: {
          carrier: string | null
          created_at: string | null
          created_by: string | null
          inspection_date: string | null
          inspection_status: string | null
          inspector: string | null
          receipt_date: string
          receipt_id: string
          receipt_number: string
          receipt_status: string | null
          remark: string | null
          supplier_id: string | null
          tenant_id: string | null
          tracking_number: string | null
          updated_at: string | null
        }
        Insert: {
          carrier?: string | null
          created_at?: string | null
          created_by?: string | null
          inspection_date?: string | null
          inspection_status?: string | null
          inspector?: string | null
          receipt_date: string
          receipt_id?: string
          receipt_number: string
          receipt_status?: string | null
          remark?: string | null
          supplier_id?: string | null
          tenant_id?: string | null
          tracking_number?: string | null
          updated_at?: string | null
        }
        Update: {
          carrier?: string | null
          created_at?: string | null
          created_by?: string | null
          inspection_date?: string | null
          inspection_status?: string | null
          inspector?: string | null
          receipt_date?: string
          receipt_id?: string
          receipt_number?: string
          receipt_status?: string | null
          remark?: string | null
          supplier_id?: string | null
          tenant_id?: string | null
          tracking_number?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "receipt_header_supplier_id_fkey"
            columns: ["supplier_id"]
            isOneToOne: false
            referencedRelation: "dim_supplier"
            referencedColumns: ["supplier_id"]
          },
        ]
      }
      receipt_line: {
        Row: {
          accepted_quantity: number | null
          created_at: string | null
          line_id: string
          line_number: number
          line_status: string | null
          quality_remark: string | null
          quality_status: string | null
          receipt_id: string
          received_quantity: number
          rejected_quantity: number | null
          remark: string | null
          sku_code: string | null
          sku_id: string | null
          sku_name: string | null
          source_po_id: string | null
          source_po_line_id: string | null
          tenant_id: string | null
          unit_price: number | null
          updated_at: string | null
        }
        Insert: {
          accepted_quantity?: number | null
          created_at?: string | null
          line_id?: string
          line_number: number
          line_status?: string | null
          quality_remark?: string | null
          quality_status?: string | null
          receipt_id: string
          received_quantity: number
          rejected_quantity?: number | null
          remark?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_po_id?: string | null
          source_po_line_id?: string | null
          tenant_id?: string | null
          unit_price?: number | null
          updated_at?: string | null
        }
        Update: {
          accepted_quantity?: number | null
          created_at?: string | null
          line_id?: string
          line_number?: number
          line_status?: string | null
          quality_remark?: string | null
          quality_status?: string | null
          receipt_id?: string
          received_quantity?: number
          rejected_quantity?: number | null
          remark?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_po_id?: string | null
          source_po_line_id?: string | null
          tenant_id?: string | null
          unit_price?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "receipt_line_receipt_id_fkey"
            columns: ["receipt_id"]
            isOneToOne: false
            referencedRelation: "receipt_header"
            referencedColumns: ["receipt_id"]
          },
          {
            foreignKeyName: "receipt_line_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "receipt_line_source_po_id_fkey"
            columns: ["source_po_id"]
            isOneToOne: false
            referencedRelation: "purchase_order_header"
            referencedColumns: ["po_id"]
          },
          {
            foreignKeyName: "receipt_line_source_po_line_id_fkey"
            columns: ["source_po_line_id"]
            isOneToOne: false
            referencedRelation: "purchase_order_line"
            referencedColumns: ["line_id"]
          },
        ]
      }
      report_instances: {
        Row: {
          config_id: string | null
          created_at: string | null
          generated_at: string | null
          generation_status: string | null
          instance_id: string
          key_findings: string | null
          period_end: string | null
          period_start: string | null
          recommendations: string | null
          report_data: Json | null
          report_date: string | null
          report_file_path: string | null
          report_format: string | null
          summary_metrics: Json | null
          tenant_id: string | null
        }
        Insert: {
          config_id?: string | null
          created_at?: string | null
          generated_at?: string | null
          generation_status?: string | null
          instance_id?: string
          key_findings?: string | null
          period_end?: string | null
          period_start?: string | null
          recommendations?: string | null
          report_data?: Json | null
          report_date?: string | null
          report_file_path?: string | null
          report_format?: string | null
          summary_metrics?: Json | null
          tenant_id?: string | null
        }
        Update: {
          config_id?: string | null
          created_at?: string | null
          generated_at?: string | null
          generation_status?: string | null
          instance_id?: string
          key_findings?: string | null
          period_end?: string | null
          period_start?: string | null
          recommendations?: string | null
          report_data?: Json | null
          report_date?: string | null
          report_file_path?: string | null
          report_format?: string | null
          summary_metrics?: Json | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "report_instances_config_id_fkey"
            columns: ["config_id"]
            isOneToOne: false
            referencedRelation: "periodic_report_config"
            referencedColumns: ["config_id"]
          },
          {
            foreignKeyName: "report_instances_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      sales_invoice_header: {
        Row: {
          created_at: string | null
          created_by: string | null
          currency_code: string | null
          customer_id: string | null
          discount_amount: number | null
          due_date: string | null
          invoice_date: string
          invoice_id: string
          invoice_number: string
          invoice_status: string | null
          invoice_type: string | null
          net_amount: number | null
          paid_amount: number | null
          payment_status: string | null
          payment_term: string | null
          remark: string | null
          tax_amount: number | null
          tenant_id: string | null
          total_amount: number | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          customer_id?: string | null
          discount_amount?: number | null
          due_date?: string | null
          invoice_date: string
          invoice_id?: string
          invoice_number: string
          invoice_status?: string | null
          invoice_type?: string | null
          net_amount?: number | null
          paid_amount?: number | null
          payment_status?: string | null
          payment_term?: string | null
          remark?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          customer_id?: string | null
          discount_amount?: number | null
          due_date?: string | null
          invoice_date?: string
          invoice_id?: string
          invoice_number?: string
          invoice_status?: string | null
          invoice_type?: string | null
          net_amount?: number | null
          paid_amount?: number | null
          payment_status?: string | null
          payment_term?: string | null
          remark?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sales_invoice_header_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "dim_customer"
            referencedColumns: ["customer_id"]
          },
        ]
      }
      sales_invoice_line: {
        Row: {
          created_at: string | null
          discount_amount: number | null
          invoice_id: string
          line_amount: number
          line_id: string
          line_number: number
          net_amount: number
          quantity: number
          remark: string | null
          sku_code: string | null
          sku_id: string | null
          sku_name: string | null
          source_order_id: string | null
          source_order_line_id: string | null
          source_shipment_id: string | null
          source_shipment_line_id: string | null
          tax_amount: number | null
          tax_rate: number | null
          tenant_id: string | null
          unit_price: number
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          discount_amount?: number | null
          invoice_id: string
          line_amount: number
          line_id?: string
          line_number: number
          net_amount: number
          quantity: number
          remark?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_order_id?: string | null
          source_order_line_id?: string | null
          source_shipment_id?: string | null
          source_shipment_line_id?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price: number
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          discount_amount?: number | null
          invoice_id?: string
          line_amount?: number
          line_id?: string
          line_number?: number
          net_amount?: number
          quantity?: number
          remark?: string | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_order_id?: string | null
          source_order_line_id?: string | null
          source_shipment_id?: string | null
          source_shipment_line_id?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price?: number
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sales_invoice_line_invoice_id_fkey"
            columns: ["invoice_id"]
            isOneToOne: false
            referencedRelation: "sales_invoice_header"
            referencedColumns: ["invoice_id"]
          },
          {
            foreignKeyName: "sales_invoice_line_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "sales_invoice_line_source_order_id_fkey"
            columns: ["source_order_id"]
            isOneToOne: false
            referencedRelation: "sales_order_header"
            referencedColumns: ["order_id"]
          },
          {
            foreignKeyName: "sales_invoice_line_source_order_line_id_fkey"
            columns: ["source_order_line_id"]
            isOneToOne: false
            referencedRelation: "sales_order_line"
            referencedColumns: ["line_id"]
          },
          {
            foreignKeyName: "sales_invoice_line_source_shipment_id_fkey"
            columns: ["source_shipment_id"]
            isOneToOne: false
            referencedRelation: "shipment_header"
            referencedColumns: ["shipment_id"]
          },
          {
            foreignKeyName: "sales_invoice_line_source_shipment_line_id_fkey"
            columns: ["source_shipment_line_id"]
            isOneToOne: false
            referencedRelation: "shipment_line"
            referencedColumns: ["line_id"]
          },
        ]
      }
      sales_order_header: {
        Row: {
          approved_at: string | null
          approved_by: string | null
          channel_id: string | null
          contact_person: string | null
          contact_phone: string | null
          created_at: string | null
          created_by: string | null
          currency_code: string | null
          customer_id: string | null
          delivery_address: string | null
          discount_amount: number | null
          net_amount: number | null
          order_date: string
          order_id: string
          order_number: string
          order_status: string | null
          payment_term: string | null
          remark: string | null
          tax_amount: number | null
          tenant_id: string | null
          total_amount: number | null
          updated_at: string | null
        }
        Insert: {
          approved_at?: string | null
          approved_by?: string | null
          channel_id?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          customer_id?: string | null
          delivery_address?: string | null
          discount_amount?: number | null
          net_amount?: number | null
          order_date: string
          order_id?: string
          order_number: string
          order_status?: string | null
          payment_term?: string | null
          remark?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Update: {
          approved_at?: string | null
          approved_by?: string | null
          channel_id?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          created_by?: string | null
          currency_code?: string | null
          customer_id?: string | null
          delivery_address?: string | null
          discount_amount?: number | null
          net_amount?: number | null
          order_date?: string
          order_id?: string
          order_number?: string
          order_status?: string | null
          payment_term?: string | null
          remark?: string | null
          tax_amount?: number | null
          tenant_id?: string | null
          total_amount?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sales_order_header_channel_id_fkey"
            columns: ["channel_id"]
            isOneToOne: false
            referencedRelation: "dim_channel"
            referencedColumns: ["channel_id"]
          },
          {
            foreignKeyName: "sales_order_header_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "dim_customer"
            referencedColumns: ["customer_id"]
          },
        ]
      }
      sales_order_line: {
        Row: {
          created_at: string | null
          discount_amount: number | null
          discount_rate: number | null
          invoiced_quantity: number | null
          line_amount: number
          line_id: string
          line_number: number
          line_status: string | null
          net_amount: number
          order_id: string
          promised_delivery_date: string | null
          quantity: number
          remark: string | null
          requested_delivery_date: string | null
          shipped_quantity: number | null
          sku_code: string | null
          sku_id: string | null
          sku_name: string | null
          tax_amount: number | null
          tax_rate: number | null
          tenant_id: string | null
          unit_price: number
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          discount_amount?: number | null
          discount_rate?: number | null
          invoiced_quantity?: number | null
          line_amount: number
          line_id?: string
          line_number: number
          line_status?: string | null
          net_amount: number
          order_id: string
          promised_delivery_date?: string | null
          quantity: number
          remark?: string | null
          requested_delivery_date?: string | null
          shipped_quantity?: number | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price: number
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          discount_amount?: number | null
          discount_rate?: number | null
          invoiced_quantity?: number | null
          line_amount?: number
          line_id?: string
          line_number?: number
          line_status?: string | null
          net_amount?: number
          order_id?: string
          promised_delivery_date?: string | null
          quantity?: number
          remark?: string | null
          requested_delivery_date?: string | null
          shipped_quantity?: number | null
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          tax_amount?: number | null
          tax_rate?: number | null
          tenant_id?: string | null
          unit_price?: number
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sales_order_line_order_id_fkey"
            columns: ["order_id"]
            isOneToOne: false
            referencedRelation: "sales_order_header"
            referencedColumns: ["order_id"]
          },
          {
            foreignKeyName: "sales_order_line_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
        ]
      }
      shipment_header: {
        Row: {
          actual_delivery_date: string | null
          carrier: string | null
          contact_person: string | null
          contact_phone: string | null
          created_at: string | null
          created_by: string | null
          customer_id: string | null
          delivery_address: string | null
          planned_delivery_date: string | null
          remark: string | null
          shipment_date: string
          shipment_id: string
          shipment_number: string
          shipment_status: string | null
          shipping_method: string | null
          tenant_id: string | null
          tracking_number: string | null
          updated_at: string | null
        }
        Insert: {
          actual_delivery_date?: string | null
          carrier?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          created_by?: string | null
          customer_id?: string | null
          delivery_address?: string | null
          planned_delivery_date?: string | null
          remark?: string | null
          shipment_date: string
          shipment_id?: string
          shipment_number: string
          shipment_status?: string | null
          shipping_method?: string | null
          tenant_id?: string | null
          tracking_number?: string | null
          updated_at?: string | null
        }
        Update: {
          actual_delivery_date?: string | null
          carrier?: string | null
          contact_person?: string | null
          contact_phone?: string | null
          created_at?: string | null
          created_by?: string | null
          customer_id?: string | null
          delivery_address?: string | null
          planned_delivery_date?: string | null
          remark?: string | null
          shipment_date?: string
          shipment_id?: string
          shipment_number?: string
          shipment_status?: string | null
          shipping_method?: string | null
          tenant_id?: string | null
          tracking_number?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "shipment_header_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "dim_customer"
            referencedColumns: ["customer_id"]
          },
        ]
      }
      shipment_line: {
        Row: {
          created_at: string | null
          line_id: string
          line_number: number
          line_status: string | null
          remark: string | null
          shipment_id: string
          shipped_quantity: number
          sku_code: string | null
          sku_id: string | null
          sku_name: string | null
          source_order_id: string | null
          source_order_line_id: string | null
          tenant_id: string | null
          unit_price: number | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          line_id?: string
          line_number: number
          line_status?: string | null
          remark?: string | null
          shipment_id: string
          shipped_quantity: number
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_order_id?: string | null
          source_order_line_id?: string | null
          tenant_id?: string | null
          unit_price?: number | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          line_id?: string
          line_number?: number
          line_status?: string | null
          remark?: string | null
          shipment_id?: string
          shipped_quantity?: number
          sku_code?: string | null
          sku_id?: string | null
          sku_name?: string | null
          source_order_id?: string | null
          source_order_line_id?: string | null
          tenant_id?: string | null
          unit_price?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "shipment_line_shipment_id_fkey"
            columns: ["shipment_id"]
            isOneToOne: false
            referencedRelation: "shipment_header"
            referencedColumns: ["shipment_id"]
          },
          {
            foreignKeyName: "shipment_line_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
          },
          {
            foreignKeyName: "shipment_line_source_order_id_fkey"
            columns: ["source_order_id"]
            isOneToOne: false
            referencedRelation: "sales_order_header"
            referencedColumns: ["order_id"]
          },
          {
            foreignKeyName: "shipment_line_source_order_line_id_fkey"
            columns: ["source_order_line_id"]
            isOneToOne: false
            referencedRelation: "sales_order_line"
            referencedColumns: ["line_id"]
          },
        ]
      }
      tenants: {
        Row: {
          created_at: string | null
          industry: string | null
          is_active: boolean | null
          tenant_code: string
          tenant_id: string
          tenant_name: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          industry?: string | null
          is_active?: boolean | null
          tenant_code: string
          tenant_id?: string
          tenant_name: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          industry?: string | null
          is_active?: boolean | null
          tenant_code?: string
          tenant_id?: string
          tenant_name?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      user_profiles: {
        Row: {
          created_at: string | null
          department: string | null
          email: string
          full_name: string | null
          is_active: boolean | null
          phone: string | null
          tenant_id: string | null
          updated_at: string | null
          user_id: string
        }
        Insert: {
          created_at?: string | null
          department?: string | null
          email: string
          full_name?: string | null
          is_active?: boolean | null
          phone?: string | null
          tenant_id?: string | null
          updated_at?: string | null
          user_id: string
        }
        Update: {
          created_at?: string | null
          department?: string | null
          email?: string
          full_name?: string | null
          is_active?: boolean | null
          phone?: string | null
          tenant_id?: string | null
          updated_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_profiles_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
      user_roles: {
        Row: {
          granted_at: string | null
          granted_by: string | null
          id: string
          role: Database["public"]["Enums"]["app_role"]
          tenant_id: string | null
          user_id: string
        }
        Insert: {
          granted_at?: string | null
          granted_by?: string | null
          id?: string
          role: Database["public"]["Enums"]["app_role"]
          tenant_id?: string | null
          user_id: string
        }
        Update: {
          granted_at?: string | null
          granted_by?: string | null
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          tenant_id?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_roles_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["tenant_id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      get_user_tenant_id: { Args: { _user_id: string }; Returns: string }
      has_cross_tenant_access: {
        Args: { _tenant_id: string; _user_id: string }
        Returns: boolean
      }
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"]
          _user_id: string
        }
        Returns: boolean
      }
    }
    Enums: {
      app_role: "admin" | "analyst" | "manager" | "operator"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: ["admin", "analyst", "manager", "operator"],
    },
  },
} as const
