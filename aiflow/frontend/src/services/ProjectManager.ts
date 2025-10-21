/**
 * 项目管理服务
 * 负责多项目的缓存、切换、导入和导出
 * 支持多项目存储和导出功能
 */

export interface ProjectInfo {
  id: string; // 唯一ID
  name: string; // 项目名称
  timestamp: string; // 保存时间
  protocol_version: string; // 协议版本
  data: any; // 完整的分析数据
}

const STORAGE_KEY = 'aiflow_projects';
const CURRENT_PROJECT_KEY = 'aiflow_current_project';

export class ProjectManager {
  /**
   * 获取所有保存的项目列表
   */
  static getAllProjects(): ProjectInfo[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {return [];}
      return JSON.parse(stored);
    } catch (error) {
      console.error('❌ 读取项目列表失败:', error);
      return [];
    }
  }

  /**
   * 保存项目到缓存
   */
  static saveProject(data: any): ProjectInfo {
    const projectName = data.metadata?.project_name || data.project_name || 'Unknown Project';
    const protocolVersion = data.metadata?.protocol_version || data.protocol_version || '2.0.0';
    const timestamp = new Date().toISOString();

    // 生成唯一ID
    const id = `${projectName}_${Date.now()}`;

    const projectInfo: ProjectInfo = {
      id,
      name: projectName,
      timestamp,
      protocol_version: protocolVersion,
      data
    };

    // 获取现有项目列表
    const projects = this.getAllProjects();

    // 检查是否已存在同名项目（更新而非新增）
    const existingIndex = projects.findIndex(p => p.name === projectName);

    if (existingIndex >= 0) {
      // 更新现有项目
      projects[existingIndex] = projectInfo;
      console.log(`🔄 更新项目: ${projectName}`);
    } else {
      // 添加新项目
      projects.push(projectInfo);
      console.log(`➕ 新增项目: ${projectName}`);
    }

    // 保存到 localStorage
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
      console.log(`✅ 项目已保存: ${projectName} (${id})`);
      return projectInfo;
    } catch (error) {
      console.error('❌ 保存项目失败:', error);
      throw new Error('项目保存失败，可能是存储空间不足');
    }
  }

  /**
   * 获取当前选中的项目ID
   */
  static getCurrentProjectId(): string | null {
    return localStorage.getItem(CURRENT_PROJECT_KEY);
  }

  /**
   * 设置当前选中的项目
   */
  static setCurrentProject(projectId: string): void {
    localStorage.setItem(CURRENT_PROJECT_KEY, projectId);
    console.log(`🎯 切换到项目: ${projectId}`);
  }

  /**
   * 根据ID获取项目
   */
  static getProjectById(id: string): ProjectInfo | null {
    const projects = this.getAllProjects();
    return projects.find(p => p.id === id) || null;
  }

  /**
   * 删除项目
   */
  static deleteProject(id: string): boolean {
    try {
      const projects = this.getAllProjects();
      const filtered = projects.filter(p => p.id !== id);

      if (filtered.length === projects.length) {
        console.warn(`⚠️ 项目不存在: ${id}`);
        return false;
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      console.log(`🗑️ 已删除项目: ${id}`);

      // 如果删除的是当前项目，清除当前项目标记
      if (this.getCurrentProjectId() === id) {
        localStorage.removeItem(CURRENT_PROJECT_KEY);
      }

      return true;
    } catch (error) {
      console.error('❌ 删除项目失败:', error);
      return false;
    }
  }

  /**
   * 导出项目为 JSON 文件
   */
  static exportProject(id: string): void {
    const project = this.getProjectById(id);
    if (!project) {
      console.error(`❌ 项目不存在: ${id}`);
      return;
    }

    // 创建 JSON Blob
    const jsonString = JSON.stringify(project.data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    // 创建下载链接并触发下载
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project.name}-analysis.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log(`📥 已导出项目: ${project.name}`);
  }

  /**
   * 从文件导入项目
   */
  static importProject(file: File): Promise<ProjectInfo> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target?.result as string);
          const projectInfo = this.saveProject(jsonData);
          console.log(`📤 已导入项目: ${projectInfo.name}`);
          resolve(projectInfo);
        } catch (error) {
          console.error('❌ 导入项目失败:', error);
          reject(new Error('JSON 文件格式错误'));
        }
      };

      reader.onerror = () => {
        reject(new Error('文件读取失败'));
      };

      reader.readAsText(file);
    });
  }

  /**
   * 清空所有项目（慎用）
   */
  static clearAllProjects(): void {
    if (confirm('⚠️ 确定要清空所有项目吗？此操作不可恢复！')) {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(CURRENT_PROJECT_KEY);
      console.log('🧹 已清空所有项目');
    }
  }

  /**
   * 获取存储使用情况
   */
  static getStorageInfo(): { used: number; total: number; percentage: number } {
    try {
      // 计算所有 localStorage 数据的总大小
      let totalSize = 0;

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) {
          const value = localStorage.getItem(key) || '';
          // 计算 key + value 的总大小
          totalSize += new Blob([key]).size;
          totalSize += new Blob([value]).size;
        }
      }

      const total = 5 * 1024 * 1024; // localStorage 通常限制 5MB
      const percentage = (totalSize / total) * 100;

      console.log('📊 存储使用情况:', {
        used: totalSize,
        usedFormatted: this.formatBytes(totalSize),
        total: total,
        totalFormatted: this.formatBytes(total),
        percentage: percentage.toFixed(2) + '%',
        itemCount: localStorage.length
      });

      return { used: totalSize, total, percentage };
    } catch (error) {
      console.error('❌ 获取存储信息失败:', error);
      return { used: 0, total: 5 * 1024 * 1024, percentage: 0 };
    }
  }

  /**
   * 格式化字节大小
   */
  static formatBytes(bytes: number): string {
    if (bytes === 0) {return '0 B';}
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}
