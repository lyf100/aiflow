#!/usr/bin/env node

/**
 * ClaudeFlow MCP 服务器 npm 安装脚本
 *
 * 提供跨平台的 npm 安装接口
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

// 主安装函数
async function install() {
  printHeader('ClaudeFlow MCP 服务器 npm 安装');

  // 检查 Python
  printInfo('检查 Python 环境...');
  const pythonCmd = getPythonCommand();

  if (!pythonCmd) {
    printError('未找到 Python 环境');
    printError('请安装 Python 3.8 或更高版本');
    process.exit(1);
  }

  printSuccess(`找到 Python: ${pythonCmd}`);

  // 定位安装脚本
  const scriptDir = path.dirname(__dirname);
  const installScript = path.join(scriptDir, 'install_mcp.py');

  if (!fs.existsSync(installScript)) {
    printError(`安装脚本不存在: ${installScript}`);
    printError('请确保 ClaudeFlow 项目完整');
    process.exit(1);
  }

  printInfo('运行 Python 安装脚本...\n');

  // 执行 Python 安装脚本
  const child = spawn(pythonCmd, [installScript], {
    cwd: scriptDir,
    stdio: 'inherit'
  });

  child.on('error', (error) => {
    printError(`安装失败: ${error.message}`);
    process.exit(1);
  });

  child.on('close', (code) => {
    if (code !== 0) {
      printError(`安装失败，退出码: ${code}`);
      process.exit(code);
    }

    console.log('\n');
    printSuccess('npm 安装完成！');
    printInfo('后续操作:');
    console.log('  1. 重启 Claude Desktop');
    console.log('  2. 开始使用 ClaudeFlow MCP 工具\n');
  });
}

// 运行安装
install().catch((error) => {
  printError(`安装过程中发生错误: ${error.message}`);
  process.exit(1);
});