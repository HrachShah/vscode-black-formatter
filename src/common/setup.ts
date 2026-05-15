// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import * as path from 'path';
import * as fs from 'fs-extra';
import { EXTENSION_ROOT_DIR } from './constants';

export interface IServerInfo {
    name: string;
    module: string;
}

export function loadServerDefaults(): IServerInfo {
    const packageJson = path.join(EXTENSION_ROOT_DIR, 'package.json');
    let content: string;
    try {
        content = fs.readFileSync(packageJson).toString();
    } catch (err: unknown) {
        throw new Error(`Failed to read package.json at ${packageJson}: ${err}`);
    }
    let config: { serverInfo?: IServerInfo };
    try {
        config = JSON.parse(content);
    } catch (err: unknown) {
        throw new Error(`Failed to parse package.json at ${packageJson}: ${err}`);
    }
    if (!config.serverInfo) {
        throw new Error(`package.json at ${packageJson} is missing the 'serverInfo' field`);
    }
    return config.serverInfo;
}
