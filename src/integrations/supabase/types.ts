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
      bridge_attribution: {
        Row: {
          attribution_id: string
          attribution_value: number | null
          created_at: string | null
          order_id: string | null
          shapley_value: number | null
          touchpoint_id: string | null
          touchpoint_type: string | null
        }
        Insert: {
          attribution_id?: string
          attribution_value?: number | null
          created_at?: string | null
          order_id?: string | null
          shapley_value?: number | null
          touchpoint_id?: string | null
          touchpoint_type?: string | null
        }
        Update: {
          attribution_id?: string
          attribution_value?: number | null
          created_at?: string | null
          order_id?: string | null
          shapley_value?: number | null
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
        ]
      }
      bridge_conv_vpt: {
        Row: {
          bridge_id: string
          conv_channel_id: string | null
          conversion_count: number | null
          created_at: string | null
          vpt_id: string | null
        }
        Insert: {
          bridge_id?: string
          conv_channel_id?: string | null
          conversion_count?: number | null
          created_at?: string | null
          vpt_id?: string | null
        }
        Update: {
          bridge_id?: string
          conv_channel_id?: string | null
          conversion_count?: number | null
          created_at?: string | null
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
          vpt_id: string | null
        }
        Insert: {
          bridge_id?: string
          created_at?: string | null
          impression_count?: number | null
          media_channel_id?: string | null
          reach_count?: number | null
          vpt_id?: string | null
        }
        Update: {
          bridge_id?: string
          created_at?: string | null
          impression_count?: number | null
          media_channel_id?: string | null
          reach_count?: number | null
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
          weight: number | null
        }
        Insert: {
          bridge_id?: string
          created_at?: string | null
          pft_id?: string | null
          sku_id?: string | null
          weight?: number | null
        }
        Update: {
          bridge_id?: string
          created_at?: string | null
          pft_id?: string | null
          sku_id?: string | null
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
        ]
      }
      bridge_vpt_pft: {
        Row: {
          bridge_id: string
          correlation: number | null
          created_at: string | null
          pft_id: string | null
          vpt_id: string | null
        }
        Insert: {
          bridge_id?: string
          correlation?: number | null
          created_at?: string | null
          pft_id?: string | null
          vpt_id?: string | null
        }
        Update: {
          bridge_id?: string
          correlation?: number | null
          created_at?: string | null
          pft_id?: string | null
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
            foreignKeyName: "bridge_vpt_pft_vpt_id_fkey"
            columns: ["vpt_id"]
            isOneToOne: false
            referencedRelation: "dim_vpt"
            referencedColumns: ["vpt_id"]
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
      dim_activity: {
        Row: {
          activity_code: string
          activity_id: string
          activity_name: string
          activity_type: string | null
          created_at: string | null
          description: string | null
        }
        Insert: {
          activity_code: string
          activity_id?: string
          activity_name: string
          activity_type?: string | null
          created_at?: string | null
          description?: string | null
        }
        Update: {
          activity_code?: string
          activity_id?: string
          activity_name?: string
          activity_type?: string | null
          created_at?: string | null
          description?: string | null
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
        }
        Insert: {
          channel_code: string
          channel_id?: string
          channel_name: string
          channel_type?: string | null
          created_at?: string | null
          description?: string | null
        }
        Update: {
          channel_code?: string
          channel_id?: string
          channel_name?: string
          channel_type?: string | null
          created_at?: string | null
          description?: string | null
        }
        Relationships: []
      }
      dim_conv_channel: {
        Row: {
          channel_code: string
          channel_name: string
          channel_type: string | null
          conv_channel_id: string
          created_at: string | null
        }
        Insert: {
          channel_code: string
          channel_name: string
          channel_type?: string | null
          conv_channel_id?: string
          created_at?: string | null
        }
        Update: {
          channel_code?: string
          channel_name?: string
          channel_type?: string | null
          conv_channel_id?: string
          created_at?: string | null
        }
        Relationships: []
      }
      dim_customer: {
        Row: {
          created_at: string | null
          customer_code: string
          customer_id: string
          customer_name: string
          customer_segment: string | null
          region: string | null
        }
        Insert: {
          created_at?: string | null
          customer_code: string
          customer_id?: string
          customer_name: string
          customer_segment?: string | null
          region?: string | null
        }
        Update: {
          created_at?: string | null
          customer_code?: string
          customer_id?: string
          customer_name?: string
          customer_segment?: string | null
          region?: string | null
        }
        Relationships: []
      }
      dim_media_channel: {
        Row: {
          channel_code: string
          channel_name: string
          channel_type: string | null
          cost_per_impression: number | null
          created_at: string | null
          media_channel_id: string
        }
        Insert: {
          channel_code: string
          channel_name: string
          channel_type?: string | null
          cost_per_impression?: number | null
          created_at?: string | null
          media_channel_id?: string
        }
        Update: {
          channel_code?: string
          channel_name?: string
          channel_type?: string | null
          cost_per_impression?: number | null
          created_at?: string | null
          media_channel_id?: string
        }
        Relationships: []
      }
      dim_pft: {
        Row: {
          created_at: string | null
          description: string | null
          pft_category: string | null
          pft_code: string
          pft_id: string
          pft_name: string
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          pft_category?: string | null
          pft_code: string
          pft_id?: string
          pft_name: string
        }
        Update: {
          created_at?: string | null
          description?: string | null
          pft_category?: string | null
          pft_code?: string
          pft_id?: string
          pft_name?: string
        }
        Relationships: []
      }
      dim_sku: {
        Row: {
          category: string | null
          created_at: string | null
          sku_code: string
          sku_id: string
          sku_name: string
          unit_price: number | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          sku_code: string
          sku_id?: string
          sku_name: string
          unit_price?: number | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          sku_code?: string
          sku_id?: string
          sku_name?: string
          unit_price?: number | null
        }
        Relationships: []
      }
      dim_supplier: {
        Row: {
          created_at: string | null
          rating: number | null
          region: string | null
          supplier_code: string
          supplier_id: string
          supplier_name: string
        }
        Insert: {
          created_at?: string | null
          rating?: number | null
          region?: string | null
          supplier_code: string
          supplier_id?: string
          supplier_name: string
        }
        Update: {
          created_at?: string | null
          rating?: number | null
          region?: string | null
          supplier_code?: string
          supplier_id?: string
          supplier_name?: string
        }
        Relationships: []
      }
      dim_vpt: {
        Row: {
          created_at: string | null
          description: string | null
          vpt_category: string | null
          vpt_code: string
          vpt_id: string
          vpt_name: string
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          vpt_category?: string | null
          vpt_code: string
          vpt_id?: string
          vpt_name: string
        }
        Update: {
          created_at?: string | null
          description?: string | null
          vpt_category?: string | null
          vpt_code?: string
          vpt_id?: string
          vpt_name?: string
        }
        Relationships: []
      }
      fact_expense: {
        Row: {
          activity_id: string | null
          created_at: string | null
          expense_amount: number
          expense_date: string
          expense_id: string
          expense_type: string | null
        }
        Insert: {
          activity_id?: string | null
          created_at?: string | null
          expense_amount: number
          expense_date: string
          expense_id?: string
          expense_type?: string | null
        }
        Update: {
          activity_id?: string | null
          created_at?: string | null
          expense_amount?: number
          expense_date?: string
          expense_id?: string
          expense_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fact_expense_activity_id_fkey"
            columns: ["activity_id"]
            isOneToOne: false
            referencedRelation: "dim_activity"
            referencedColumns: ["activity_id"]
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
        }
        Insert: {
          cost?: number | null
          created_at?: string | null
          produce_date: string
          produce_id?: string
          quantity: number
          sku_id?: string | null
        }
        Update: {
          cost?: number | null
          created_at?: string | null
          produce_date?: string
          produce_id?: string
          quantity?: number
          sku_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fact_produce_sku_id_fkey"
            columns: ["sku_id"]
            isOneToOne: false
            referencedRelation: "dim_sku"
            referencedColumns: ["sku_id"]
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
        }
        Insert: {
          created_at?: string | null
          sku_id?: string | null
          supplier_fact_id?: string
          supplier_id?: string | null
          supply_amount?: number | null
          supply_date: string
        }
        Update: {
          created_at?: string | null
          sku_id?: string | null
          supplier_fact_id?: string
          supplier_id?: string | null
          supply_amount?: number | null
          supply_date?: string
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
        ]
      }
      fact_voice: {
        Row: {
          created_at: string | null
          customer_id: string | null
          satisfaction_score: number | null
          sentiment: string | null
          sku_id: string | null
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
