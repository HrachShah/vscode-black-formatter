// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { Disposable, workspace } from 'vscode';
import { BLACK_CONFIG_FILES } from './constants';
import { traceError, traceLog } from './logging';

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
let pendingCallback: (() => void) | null = null;
const DEBOUNCE_DELAY_MS = 200;

export function createConfigFileWatchers(onConfigChanged: () => Promise<void>): Disposable[] {
    return BLACK_CONFIG_FILES.map((pattern) => {
        const watcher = workspace.createFileSystemWatcher(`**/${pattern}`);
        let disposed = false;

        const handleEvent = (event: string) => {
            if (disposed) {
                return;
            }
            traceLog(`Black config file ${event}: ${pattern}`);
            if (debounceTimer !== null) {
                clearTimeout(debounceTimer);
                debounceTimer = null;
            }
            pendingCallback = () => {
                pendingCallback = null;
                debounceTimer = null;
                onConfigChanged().catch((e) => traceError(`Config file ${event} handler failed`, e));
            };
            debounceTimer = setTimeout(pendingCallback, DEBOUNCE_DELAY_MS);
        };

        const changeDisposable = watcher.onDidChange(() => handleEvent('changed'));
        const createDisposable = watcher.onDidCreate(() => handleEvent('created'));
        const deleteDisposable = watcher.onDidDelete(() => handleEvent('deleted'));

        return {
            dispose(): void {
                disposed = true;
                if (debounceTimer !== null) {
                    clearTimeout(debounceTimer);
                    debounceTimer = null;
                    pendingCallback = null;
                }
                changeDisposable.dispose();
                createDisposable.dispose();
                deleteDisposable.dispose();
                watcher.dispose();
            },
        };
    });
}
