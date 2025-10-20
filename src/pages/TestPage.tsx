import { RawDataUploader } from '@/components/DataImport/RawDataUploader';
import { ControllableFactsManager } from '@/components/BusinessFacts/ControllableFactsManager';
import { EvaluationPanel } from '@/components/ManagerEvaluation/EvaluationPanel';
import { CycleMonitor } from '@/components/DecisionCycle/CycleMonitor';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          BMOS 系统测试页面
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RawDataUploader />
          <EvaluationPanel analysisId="test-analysis-123" />
        </div>
        
        <ControllableFactsManager />
        <CycleMonitor />
      </div>
    </div>
  );
}
