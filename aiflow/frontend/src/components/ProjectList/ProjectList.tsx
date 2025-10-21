import { useState, useEffect } from 'react';
import { ProjectManager, ProjectInfo } from '../../services/ProjectManager';
import './ProjectList.css';

interface ProjectListProps {
  onProjectSelect: (projectData: any) => void;
  currentProjectName?: string;
}

export const ProjectList = ({ onProjectSelect, currentProjectName }: ProjectListProps) => {
  const [projects, setProjects] = useState<ProjectInfo[]>([]);
  const [storageInfo, setStorageInfo] = useState({ used: 0, total: 0, percentage: 0 });
  const [showPanel, setShowPanel] = useState(false);

  // 加载项目列表
  const loadProjects = () => {
    const allProjects = ProjectManager.getAllProjects();
    setProjects(allProjects);
    setStorageInfo(ProjectManager.getStorageInfo());
    console.log(`📚 已加载 ${allProjects.length} 个项目`);
  };

  useEffect(() => {
    loadProjects();
  }, []);

  // 切换项目
  const handleSelectProject = (project: ProjectInfo) => {
    ProjectManager.setCurrentProject(project.id);
    onProjectSelect(project.data);
    setShowPanel(false);
    console.log(`✅ 已切换到项目: ${project.name}`);
  };

  // 删除项目
  const handleDeleteProject = (e: React.MouseEvent, projectId: string) => {
    e.stopPropagation();
    if (confirm('确定要删除这个项目吗？')) {
      ProjectManager.deleteProject(projectId);
      loadProjects();
    }
  };

  // 导出项目
  const handleExportProject = (e: React.MouseEvent, projectId: string) => {
    e.stopPropagation();
    ProjectManager.exportProject(projectId);
  };

  // 导入项目
  const handleImportProject = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        try {
          const projectInfo = await ProjectManager.importProject(file);
          loadProjects();
          alert(`✅ 成功导入项目: ${projectInfo.name}`);
        } catch (error) {
          alert(`❌ 导入失败: ${(error as Error).message}`);
        }
      }
    };
    input.click();
  };

  // 格式化文件大小
  const formatBytes = (bytes: number) => {
    if (bytes === 0) {return '0 B';}
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <>
      {/* 项目管理按钮 */}
      <button
        className="project-manager-toggle"
        onClick={() => setShowPanel(!showPanel)}
        title="项目管理"
      >
        📁 项目 ({projects.length})
      </button>

      {/* 项目面板 */}
      {showPanel && (
        <div className="project-panel-overlay" onClick={() => setShowPanel(false)}>
          <div className="project-panel" onClick={(e) => e.stopPropagation()}>
            <div className="project-panel-header">
              <h2>📁 项目管理</h2>
              <button
                className="close-button"
                onClick={() => setShowPanel(false)}
              >
                ✕
              </button>
            </div>

            {/* 存储信息 */}
            <div className="storage-info">
              <div className="storage-bar">
                <div
                  className="storage-bar-fill"
                  style={{ width: `${Math.min(storageInfo.percentage, 100)}%` }}
                />
              </div>
              <div className="storage-text">
                存储使用: {formatBytes(storageInfo.used)} / {formatBytes(storageInfo.total)}
                ({storageInfo.percentage.toFixed(1)}%)
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="project-actions">
              <button
                className="action-button import"
                onClick={handleImportProject}
              >
                📤 导入项目
              </button>
              <button
                className="action-button clear"
                onClick={() => {
                  ProjectManager.clearAllProjects();
                  loadProjects();
                }}
              >
                🧹 清空所有
              </button>
            </div>

            {/* 项目列表 */}
            <div className="project-list">
              {projects.length === 0 ? (
                <div className="empty-state">
                  <p>📭 暂无保存的项目</p>
                  <p className="hint">运行分析后会自动保存</p>
                </div>
              ) : (
                projects.map((project) => (
                  <div
                    key={project.id}
                    className={`project-item ${project.name === currentProjectName ? 'active' : ''}`}
                    onClick={() => handleSelectProject(project)}
                  >
                    <div className="project-info">
                      <div className="project-name">
                        {project.name}
                        {project.name === currentProjectName && (
                          <span className="current-badge">当前</span>
                        )}
                      </div>
                      <div className="project-meta">
                        <span className="protocol-version">v{project.protocol_version}</span>
                        <span className="timestamp">
                          {new Date(project.timestamp).toLocaleString('zh-CN')}
                        </span>
                      </div>
                    </div>
                    <div className="project-actions-inline">
                      <button
                        className="icon-button export"
                        onClick={(e) => handleExportProject(e, project.id)}
                        title="导出项目"
                      >
                        📥
                      </button>
                      <button
                        className="icon-button delete"
                        onClick={(e) => handleDeleteProject(e, project.id)}
                        title="删除项目"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
