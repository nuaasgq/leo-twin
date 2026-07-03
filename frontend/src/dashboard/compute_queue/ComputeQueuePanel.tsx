import { memo } from "react";

import { TaskState } from "../../core/event_types";
import { ComputeNodeRenderState, WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface ComputeQueueSummary {
  runningTasks: number;
  finishedTasks: number;
  totalRequests: number;
  unfinishedTasks: number;
  availableRoutes: number;
  waitingForNetwork: number;
  computeNodes: number;
  busiestNodeId: string;
  averageLoadRatio: number;
  computeSchedulingPolicy: string;
  computeSchedulingPolicyLabel: string;
  nodeRows: readonly ComputeNodeQueueRow[];
  taskRows: readonly ComputeTaskRow[];
}

export interface ComputeNodeQueueRow {
  nodeId: string;
  runningTasks: number;
  finishedTasks: number;
  capacity: number;
  availableCapacity: number;
  loadRatio: number;
  status: string;
}

export interface ComputeTaskRow {
  taskId: string;
  nodeId: string;
  progress: number;
  status: string;
}

type ComputeQueueSnapshot = Pick<
  WorldSnapshot,
  "active_tasks" | "compute_nodes" | "routes" | "scenario_config"
>;

export const ComputeQueuePanel = memo(function ComputeQueuePanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildComputeQueueSummary(snapshot);

  return (
    <section className="dashboard-section compute-queue-panel" aria-label="算力队列">
      <div className="section-title">算力队列</div>
      <div className="kpi-grid wide">
        <KpiPanel label="运行任务" value={String(summary.runningTasks)} />
        <KpiPanel label="已完成" value={String(summary.finishedTasks)} />
        <KpiPanel label="未完成" value={String(summary.unfinishedTasks)} />
        <KpiPanel label="网络等待" value={String(summary.waitingForNetwork)} />
        <KpiPanel label="可用路由" value={String(summary.availableRoutes)} />
        <KpiPanel label="节点数" value={String(summary.computeNodes)} />
        <KpiPanel label="平均负载" value={formatPercent(summary.averageLoadRatio)} />
        <KpiPanel label="调度策略" value={summary.computeSchedulingPolicyLabel} />
      </div>
      <div className="compute-table" aria-label="算力节点明细">
        {summary.nodeRows.map((row) => (
          <div className="compute-table-row" key={row.nodeId}>
            <span>{row.nodeId}</span>
            <span>
              {formatStatus(row.status)} · {formatPercent(row.loadRatio)}
            </span>
            <strong>
              {formatNumber(row.availableCapacity)} / {formatNumber(row.capacity)}
            </strong>
          </div>
        ))}
      </div>
      <div className="task-strip" aria-label="当前任务">
        {summary.taskRows.map((row) => (
          <div className="task-strip-row" key={row.taskId}>
            <span>{row.taskId}</span>
            <span>{row.nodeId}</span>
            <strong>{(row.progress * 100).toFixed(0)}%</strong>
          </div>
        ))}
      </div>
    </section>
  );
});

export function buildComputeQueueSummary(
  snapshot: ComputeQueueSnapshot
): ComputeQueueSummary {
  const nodeRows = snapshot.compute_nodes
    .slice()
    .sort(compareComputeNodes)
    .map((node) => ({
      nodeId: node.node_id,
      runningTasks: node.running_tasks,
      finishedTasks: node.finished_tasks,
      capacity: node.capacity,
      availableCapacity: node.available_capacity,
      loadRatio: node.load_ratio,
      status: node.status
    }));
  const taskRows = snapshot.active_tasks
    .slice()
    .sort(compareTasks)
    .slice(0, 5)
    .map((task) => ({
      taskId: task.task_id,
      nodeId: task.node_id,
      progress: task.progress,
      status: task.status
    }));
  const runningTasks = nodeRows.reduce((total, row) => total + row.runningTasks, 0);
  const finishedTasks = nodeRows.reduce((total, row) => total + row.finishedTasks, 0);
  const totalRequests = snapshot.routes.length;
  const availableRoutes = snapshot.routes.filter((route) => route.available).length;
  const waitingForNetwork = totalRequests - availableRoutes;
  const unfinishedTasks = Math.max(0, totalRequests - finishedTasks);
  const busiest = nodeRows[0];
  const computeSchedulingPolicy =
    snapshot.scenario_config?.scenario?.compute_scheduling_policy ?? "FIFO";

  return {
    runningTasks,
    finishedTasks,
    totalRequests,
    unfinishedTasks,
    availableRoutes,
    waitingForNetwork,
    computeNodes: nodeRows.length,
    busiestNodeId: busiest?.nodeId ?? "无",
    averageLoadRatio:
      nodeRows.length === 0
        ? 0
        : nodeRows.reduce((total, row) => total + row.loadRatio, 0) / nodeRows.length,
    computeSchedulingPolicy,
    computeSchedulingPolicyLabel: formatComputeSchedulingPolicy(computeSchedulingPolicy),
    nodeRows: nodeRows.slice(0, 5),
    taskRows
  };
}

function formatComputeSchedulingPolicy(policy: string): string {
  if (policy === "SHORTEST_JOB_FIRST") {
    return "短作业优先";
  }
  if (policy === "EARLIEST_DEADLINE_FIRST") {
    return "最早截止期优先";
  }
  return "先到先服务";
}

function compareComputeNodes(
  left: ComputeNodeRenderState,
  right: ComputeNodeRenderState
): number {
  const load = right.load_ratio - left.load_ratio;
  if (load !== 0) {
    return load;
  }
  const running = right.running_tasks - left.running_tasks;
  if (running !== 0) {
    return running;
  }
  const finished = right.finished_tasks - left.finished_tasks;
  if (finished !== 0) {
    return finished;
  }
  return left.node_id.localeCompare(right.node_id);
}

function compareTasks(left: TaskState, right: TaskState): number {
  const byNode = left.node_id.localeCompare(right.node_id);
  if (byNode !== 0) {
    return byNode;
  }
  return left.task_id.localeCompare(right.task_id);
}

function formatStatus(status: string): string {
  if (status === "BUSY") {
    return "忙碌";
  }
  if (status === "IDLE") {
    return "空闲";
  }
  return status;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

function formatNumber(value: number): string {
  return value.toFixed(value >= 100 ? 0 : 1);
}
