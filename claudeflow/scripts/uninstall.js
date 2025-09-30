#!/usr/bin/env node

/**
 * ClaudeFlow MCP 服务器 npm 卸载脚本
 *
 * 提供跨平台的 npm 卸载接口
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 颜色输出
const colors = {
  green: '\x1b[92m',
  yellow: '\x1b[93m',
  red: '\x1b[91m',
  blue: '\x1b[94m',
  bold: '\x1b[1m',
  reset: '\x1b[0m'
};

function print(msg, color = '') {
  console.log(`${color}${msg}${colors.reset}`);
}

function printHeader(msg) {
  console.log(`\n${colors.bold}${'='.repeat(60)}${colors.reset}`);
  console.log(`${colors.bold}${msg}${colors.reset}`);
  console.log(`${colors.bold}${'='.repeat(60)}${colors.reset}\n`);
}

function printSuccess(msg) {
  console.log(`${colors.green}✓${colors.reset} ${msg}`);
}

function printError(msg) {
  console.log(`${colors.red}✗${colors.reset} ${msg}`);
}

function printInfo(msg) {
  console.log(`${colors.blue}ℹ${colors.reset} ${msg}`);
}

function printWarning(msg) {
  console.log(`${colors.yellow}⚠${colors.reset} ${msg}`);
}

// 检测 Python 命令
function getPythonCommand() {
  const commands = ['python', 'python3', 'py'];

  for (const cmd of commands) {
    try {
      const result = spawn(cmd, ['--version'], { stdio: 'pipe' });
      if (result.pid) {
        return cmd;
      }
    } catch (e) {
      // 继续尝试下一个命令
    }
  }

  return null;
}

// 主卸载函数
async function uninstall() {
  printHeader('ClaudeFlow MCP 服务器 npm 卸载');

  // 检查 Python
  printInfo('检查 Python 环境...');
  const pythonCmd = getPythonCommand();

  if (!pythonCmd) {
    printError('未找到 Python 环境');
    printError('请安装 Python 3.8 或更高版本');
    process.exit(1);
  }

  printSuccess(`找到 Python: ${pythonCmd}`);

  // 定位卸载脚本
  const scriptDir = path.dirname(__dirname);
  const uninstallScript = path.join(scriptDir, 'uninstall_mcp.py');

  if (!fs.existsSync(uninstallScript)) {
    printError(`卸载脚本不存在: ${uninstallScript}`);
    printError('请确保 ClaudeFlow 项目完整');
    process.exit(1);
  }

  // 检查命令行参数
  const args = [uninstallScript];
  if (process.argv.includes('--remove-deps')) {
    args.push('--remove-deps');
    printWarning('将同时卸载依赖包');
  }

  printInfo('运行 Python 卸载脚本...\n');

  // 执行 Python 卸载脚本
  const child = spawn(pythonCmd, args, {
    cwd: scriptDir,
    stdio: 'inherit'
  });

  child.on('error', (error) => {
    printError(`卸载失败: ${error.message}`);
    process.exit(1);
  });

  child.on('close', (code) => {
    if (code !== 0) {
      printError(`卸载失败，退出码: ${code}`);
      process.exit(code);
    }

    console.log('\n');
    printSuccess('npm 卸载完成！');
    printInfo('后续操作:');
    console.log('  1. 重启 Claude Desktop 使配置生效');
    console.log('  2. 如需完全卸载，可手动删除项目目录\n');
  });
}

// 运行卸载
uninstall().catch((error) => {
  printError(`卸载过程中发生错误: ${error.message}`);
  process.exit(1);
});