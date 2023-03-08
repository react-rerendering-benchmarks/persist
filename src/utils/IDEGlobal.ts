import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import {
  ITrrackManager,
  TrrackableCell,
  TrrackableCellId,
  VegaManager
} from '../cells';
import { Executor } from '../notebook';
import { Nullable } from '../types';
import { IDELogger } from './logging';

// eslint-disable-next-line @typescript-eslint/naming-convention
export class IDEGlobal {
  static trracks: Map<TrrackableCellId, ITrrackManager>;
  static views: Map<TrrackableCellId, VegaManager>;
  static cells: Map<TrrackableCellId, TrrackableCell>;
  static renderMimeRegistry: IRenderMimeRegistry;
  static executor?: Nullable<Executor>;
  static Logger: IDELogger;
}

(window as any).IDEGlobal = IDEGlobal;
