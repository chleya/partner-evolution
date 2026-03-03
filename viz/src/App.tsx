import React, { useState, useEffect } from 'react';
import {
  Brain,
  GitBranch,
  Activity,
  Zap,
  Shield,
  Layers,
  ArrowRight,
  Box,
  Network,
  Database,
  Sparkles,
  ChevronDown,
  Eye,
  AlertTriangle,
  Clock,
  TrendingUp,
  Infinity,
  Target,
  MessageSquare,
  CheckCircle,
  Dna,
  Settings,
  Server,
  Workflow,
} from 'lucide-react';

// 动画 Section 标题组件
const SectionTitle = ({ number, title, subtitle }: { number: string; title: string; subtitle: string }) => (
  <div className="mb-12">
    <div className="flex items-center gap-4 mb-2">
      <span className="text-6xl font-bold text-cyan-400/20 font-mono">{number}</span>
      <h2 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
        {title}
      </h2>
    </div>
    <p className="text-gray-400 text-lg ml-20">{subtitle}</p>
  </div>
);

// 导航组件
const Navigation = ({ activeSection, setActiveSection }: { activeSection: string; setActiveSection: (s: string) => void }) => {
  const sections = [
    { id: 'hero', label: '首页' },
    { id: 'overview', label: '总览' },
    { id: 'evolution', label: '递归进化' },
    { id: 'twin', label: '数字孪生' },
    { id: 'diagnosis', label: '自诊断' },
    { id: 'forking', label: '版本分叉' },
    { id: 'roadmap', label: '路线图' },
  ];

  return (
    <nav className="fixed right-8 top-1/2 transform -translate-y-1/2 z-50 hidden lg:block">
      <div className="flex flex-col gap-3">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => {
              document.getElementById(section.id)?.scrollIntoView({ behavior: 'smooth' });
              setActiveSection(section.id);
            }}
            className={`group flex items-center gap-3 transition-all duration-300 ${
              activeSection === section.id ? 'opacity-100' : 'opacity-40 hover:opacity-70'
            }`}
          >
            <span className={`w-2 h-2 rounded-full transition-all duration-300 ${
              activeSection === section.id ? 'bg-cyan-400 scale-150' : 'bg-gray-500'
            }`} />
            <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
              {section.label}
            </span>
          </button>
        ))}
      </div>
    </nav>
  );
};

// 首屏区域组件
const HeroSection = () => {
  const [particles, setParticles] = useState<Array<{ x: number; y: number; size: number; delay: number }>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      delay: Math.random() * 5,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <section id="hero" className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950">
      {/* 动态背景粒子 */}
      <div className="absolute inset-0 overflow-hidden">
        {particles.map((particle, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-cyan-400/30 animate-pulse"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: particle.size,
              height: particle.size,
              animationDelay: `${particle.delay}s`,
              animationDuration: '3s',
            }}
          />
        ))}
      </div>

      {/* 网格图案 */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-8">
        <div className="text-center max-w-4xl">
          {/* 徽章 */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 mb-8">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-300 text-sm font-medium">AI 伙伴进化计划</span>
          </div>

          {/* 主标题 */}
          <h1 className="text-6xl md:text-8xl font-bold mb-6">
            <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Partner Evolution
            </span>
          </h1>

          <p className="text-2xl md:text-3xl text-gray-300 mb-4 font-light">
            从工具到伙伴的进化之路
          </p>

          <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto">
            探索 AI 系统的递归自我进化机制，构建数字孪生架构，实现自主诊断与持续优化
          </p>

          {/* 版本标签 */}
          <div className="flex justify-center gap-6 mb-12">
            <div className="px-6 py-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40">
              <span className="text-emerald-400 font-mono">v3.0</span>
              <p className="text-xs text-emerald-300/60">数字本体论</p>
            </div>
            <div className="px-6 py-3 rounded-lg bg-purple-500/20 border border-purple-500/40">
              <span className="text-purple-400 font-mono">v4.0</span>
              <p className="text-xs text-purple-300/60">递归自我进化</p>
            </div>
          </div>

          {/* CTA 按钮 */}
          <button
            onClick={() => document.getElementById('overview')?.scrollIntoView({ behavior: 'smooth' })}
            className="group relative px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full text-white font-semibold text-lg overflow-hidden transition-all duration-300 hover:scale-105"
          >
            <span className="relative z-10 flex items-center gap-2">
              开始探索 <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </span>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        </div>

        {/* 滚动指示器 */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-8 h-8 text-gray-500" />
        </div>
      </div>
    </section>
  );
};

// 总览区域组件
const OverviewSection = () => {
  const features = [
    { icon: Brain, title: '认知引擎', desc: '多模式思考框架，支持主动反思与前瞻预测', color: 'cyan' },
    { icon: Database, title: '记忆系统', desc: '三层记忆架构，智能遗忘与置信度管理', color: 'emerald' },
    { icon: Workflow, title: '编排系统', desc: 'LangGraph工作流，支持断点续传', color: 'purple' },
    { icon: Activity, title: '观测系统', desc: '实时指标采集，智能漂移检测', color: 'orange' },
    { icon: Shield, title: '安全护栏', desc: '多层防护机制，确保系统安全可控', color: 'red' },
    { icon: Infinity, title: '递归进化', desc: '自我诊断、生成、优化、迭代闭环', color: 'pink' },
  ];

  return (
    <section id="overview" className="min-h-screen py-24 px-8 bg-slate-950">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          number="01"
          title="系统架构总览"
          subtitle="六大核心模块，构建完整的AI伙伴进化系统"
        />

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-cyan-500/50 transition-all duration-300 hover:-translate-y-1"
            >
              <div className={`w-12 h-12 rounded-xl bg-${feature.color}-500/20 flex items-center justify-center mb-4`}>
                <feature.icon className={`w-6 h-6 text-${feature.color}-400`} />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.desc}</p>
            </div>
          ))}
        </div>

        {/* 架构图 */}
        <div className="mt-16 p-8 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-2xl font-semibold text-white mb-8 text-center">架构层次</h3>
          <div className="flex flex-col items-center gap-4">
            {[
              { layer: '用户交互层', color: 'pink' },
              { layer: '观测度量层', color: 'orange' },
              { layer: '核心调度层', color: 'purple' },
              { layer: '能力服务层', color: 'cyan' },
              { layer: '数据存储层', color: 'emerald' },
            ].map((item, index) => (
              <div key={index} className="flex items-center gap-4 w-full max-w-2xl">
                <div className={`w-32 text-right text-${item.color}-400 font-mono text-sm`}>
                  Layer {index + 1}
                </div>
                <div className={`flex-1 px-6 py-3 rounded-lg bg-${item.color}-500/10 border border-${item.color}-500/30 text-center text-white`}>
                  {item.layer}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

// 递归进化区域
const EvolutionSection = () => {
  const [activeStep, setActiveStep] = useState(0);
  const steps = [
    {
      title: '自诊断',
      desc: '分析交互日志，识别错误模式与质量缺陷',
      icon: Eye,
      detail: '基于多维度指标评估系统输出质量，追溯问题根因，实现自动化异常检测。'
    },
    {
      title: '合成数据',
      desc: '将诊断结果转化为高质量训练样本',
      icon: Database,
      detail: '生成黄金思维链示例，扩充训练数据集，实现数据驱动的自我提升。'
    },
    {
      title: '代码优化',
      desc: '自动改进Prompt与检索策略',
      icon: Zap,
      detail: '在受控范围内修改配置和提示词，通过A/B测试验证优化效果。'
    },
    {
      title: '版本迭代',
      desc: '并行探索多进化路径，选择最优分支',
      icon: GitBranch,
      detail: '建立版本档案，支持回溯与对比分析，实现智能化的版本选择。'
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section id="evolution" className="min-h-screen py-24 px-8 bg-gradient-to-b from-slate-950 to-purple-950/20">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          number="02"
          title="递归自我进化"
          subtitle="Ouroboros闭环：观察 → 批判 → 合成 → 优化 → 部署"
        />

        {/* 进化循环动画 */}
        <div className="relative mb-16">
          <div className="flex justify-center items-center">
            <svg viewBox="0 0 400 400" className="w-full max-w-lg">
              {/* 外环 */}
              <circle
                cx="200"
                cy="200"
                r="160"
                fill="none"
                stroke="rgba(6,182,212,0.2)"
                strokeWidth="2"
                className="animate-spin"
                style={{ animationDuration: '20s' }}
              />

              {/* 核心圆 */}
              <circle cx="200" cy="200" r="40" fill="#10B981" opacity="0.3">
                <animate attributeName="r" values="40;45;40" dur="2s" repeatCount="indefinite" />
              </circle>
              <text x="200" y="205" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">核心</text>

              {/* 连接线和节点 */}
              {steps.map((step, index) => {
                const angle = (index * 90 - 90) * (Math.PI / 180);
                const x = 200 + 130 * Math.cos(angle);
                const y = 200 + 130 * Math.sin(angle);
                const isActive = activeStep === index;

                return (
                  <g key={index}>
                    <circle
                      cx={x}
                      cy={y}
                      r={isActive ? 25 : 20}
                      fill={isActive ? '#8B5CF6' : '#1E293B'}
                      stroke={isActive ? '#8B5CF6' : '#475569'}
                      strokeWidth="2"
                      className="transition-all duration-300 cursor-pointer"
                      onClick={() => setActiveStep(index)}
                    >
                      {isActive && (
                        <animate attributeName="r" values="25;30;25" dur="1s" repeatCount="indefinite" />
                      )}
                    </circle>
                    <text
                      x={x}
                      y={y + 4}
                      textAnchor="middle"
                      fill="white"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      {index + 1}
                    </text>
                    <line
                      x1={200 + 50 * Math.cos(angle)}
                      y1={200 + 50 * Math.sin(angle)}
                      x2={x - 15 * Math.cos(angle)}
                      y2={y - 15 * Math.sin(angle)}
                      stroke={isActive ? '#8B5CF6' : '#334155'}
                      strokeWidth={isActive ? 3 : 1}
                      className="transition-all duration-300"
                    />
                  </g>
                );
              })}
            </svg>
          </div>

          {/* 步骤标签 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            {steps.map((step, index) => (
              <button
                key={index}
                onClick={() => setActiveStep(index)}
                className={`p-4 rounded-xl text-left transition-all duration-300 ${
                  activeStep === index
                    ? 'bg-purple-500/20 border border-purple-500/50'
                    : 'bg-slate-900/50 border border-slate-800 hover:border-slate-700'
                }`}
              >
                <step.icon className={`w-6 h-6 mb-2 ${activeStep === index ? 'text-purple-400' : 'text-gray-500'}`} />
                <h4 className="font-semibold text-white mb-1">{step.title}</h4>
                <p className="text-xs text-gray-400">{step.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* 详情面板 */}
        <div className="p-8 rounded-2xl bg-slate-900/80 border border-purple-500/30">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-purple-500/20">
              {React.createElement(steps[activeStep].icon, { className: "w-8 h-8 text-purple-400" })}
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-white mb-2">{steps[activeStep].title}</h3>
              <p className="text-gray-300">{steps[activeStep].detail}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// 数字孪生区域
const TwinSection = () => {
  const [hoveredComponent, setHoveredComponent] = useState<string | null>(null);
  const components = [
    { id: 'core', label: '核心引擎', status: 'active', metrics: { cpu: 45, memory: 62, latency: '12ms' } },
    { id: 'memory', label: '记忆系统', status: 'active', metrics: { cpu: 28, memory: 85, latency: '5ms' } },
    { id: 'thinking', label: '思考引擎', status: 'active', metrics: { cpu: 72, memory: 45, latency: '28ms' } },
    { id: 'orchestration', label: '编排系统', status: 'active', metrics: { cpu: 15, memory: 22, latency: '3ms' } },
  ];

  return (
    <section id="twin" className="min-h-screen py-24 px-8 bg-slate-950">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          number="03"
          title="数字孪生架构"
          subtitle="实体与虚拟镜像同步，预测未来状态"
        />

        <div className="grid lg:grid-cols-2 gap-8">
          {/* 物理世界 */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-cyan-950/30 to-slate-900 border border-cyan-500/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
              <h3 className="text-xl font-semibold text-cyan-400">物理世界 (实体)</h3>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {components.map((comp) => (
                <div
                  key={comp.id}
                  onMouseEnter={() => setHoveredComponent(comp.id)}
                  onMouseLeave={() => setHoveredComponent(null)}
                  className={`p-4 rounded-xl cursor-pointer transition-all duration-300 ${
                    hoveredComponent === comp.id
                      ? 'bg-cyan-500/20 border-cyan-500/50 transform scale-105'
                      : 'bg-slate-900/50 border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <Box className="w-5 h-5 text-cyan-400" />
                    <span className="text-xs text-cyan-300/60">{comp.status}</span>
                  </div>
                  <p className="font-medium text-white">{comp.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 虚拟世界 */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-950/30 to-slate-900 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-3 h-3 rounded-full bg-purple-400 animate-pulse" />
              <h3 className="text-xl font-semibold text-purple-400">虚拟世界 (镜像)</h3>
            </div>

            <div className="space-y-4">
              {components.map((comp) => (
                <div
                  key={comp.id}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    hoveredComponent === comp.id
                      ? 'bg-purple-500/20 border-purple-500/50'
                      : 'bg-slate-900/50 border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-white">{comp.label}</span>
                    {hoveredComponent === comp.id && (
                      <span className="text-xs text-purple-400">预测同步中...</span>
                    )}
                  </div>
                  {hoveredComponent === comp.id && (
                    <div className="grid grid-cols-3 gap-2 mt-3">
                      <div className="text-center">
                        <p className="text-xs text-gray-500">预测CPU</p>
                        <p className="text-sm font-mono text-purple-300">{comp.metrics.cpu + 5}%</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500">预测内存</p>
                        <p className="text-sm font-mono text-purple-300">{comp.metrics.memory + 3}%</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500">预测延迟</p>
                        <p className="text-sm font-mono text-purple-300">{comp.metrics.latency}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 同步状态 */}
        <div className="mt-8 p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Network className="w-6 h-6 text-cyan-400" />
              <div>
                <p className="font-medium text-white">同步状态</p>
                <p className="text-sm text-gray-400">实体与镜像实时同步</p>
              </div>
            </div>
            <div className="flex gap-8">
              <div className="text-center">
                <p className="text-2xl font-bold text-cyan-400">99.9%</p>
                <p className="text-xs text-gray-500">同步率</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-400">12ms</p>
                <p className="text-xs text-gray-500">平均延迟</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-400">24/7</p>
                <p className="text-xs text-gray-500">运行时间</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// 自诊断区域
const DiagnosisSection = () => {
  const [diagnosisPhase, setDiagnosisPhase] = useState<'idle' | 'detecting' | 'analyzing' | 'fixing' | 'resolved'>('idle');
  const [errorCount, setErrorCount] = useState(3);

  const runDiagnosis = () => {
    setDiagnosisPhase('detecting');
    setTimeout(() => setDiagnosisPhase('analyzing'), 1500);
    setTimeout(() => setDiagnosisPhase('fixing'), 3000);
    setTimeout(() => {
      setDiagnosisPhase('resolved');
      setErrorCount(0);
    }, 4500);
    setTimeout(() => setDiagnosisPhase('idle'), 6000);
  };

  return (
    <section id="diagnosis" className="min-h-screen py-24 px-8 bg-gradient-to-b from-slate-950 to-orange-950/20">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          number="04"
          title="自诊断系统"
          subtitle="自动化问题检测、根因分析与修复"
        />

        <div className="grid lg:grid-cols-2 gap-8">
          {/* 控制面板 */}
          <div className="space-y-6">
            {/* 状态指示器 */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h4 className="text-lg font-semibold text-white mb-4">系统健康状态</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">整体状态</span>
                  <div className={`px-3 py-1 rounded-full text-sm ${
                    diagnosisPhase === 'resolved' ? 'bg-green-500/20 text-green-400' :
                    diagnosisPhase === 'fixing' ? 'bg-orange-500/20 text-orange-400' :
                    diagnosisPhase === 'analyzing' ? 'bg-yellow-500/20 text-yellow-400' :
                    diagnosisPhase === 'detecting' ? 'bg-cyan-500/20 text-cyan-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {diagnosisPhase === 'idle' ? '正常' :
                     diagnosisPhase === 'detecting' ? '检测中' :
                     diagnosisPhase === 'analyzing' ? '分析中' :
                     diagnosisPhase === 'fixing' ? '修复中' : '已修复'}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">检测到的异常</span>
                  <span className={`text-xl font-bold ${errorCount > 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {errorCount}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">最后诊断时间</span>
                  <span className="text-gray-300 font-mono">
                    {diagnosisPhase === 'idle' ? '--:--:--' : new Date().toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </div>

            {/* 触发按钮 */}
            <button
              onClick={runDiagnosis}
              disabled={diagnosisPhase !== 'idle'}
              className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
                diagnosisPhase === 'idle'
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:scale-105 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              {diagnosisPhase === 'idle' ? '触发诊断' : '诊断进行中...'}
            </button>

            {/* 过程日志 */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h4 className="text-lg font-semibold text-white mb-4">诊断日志</h4>
              <div className="space-y-2 font-mono text-sm">
                <div className={`flex items-center gap-2 ${diagnosisPhase !== 'idle' ? 'text-green-400' : 'text-gray-500'}`}>
                  {diagnosisPhase !== 'idle' ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  <span>系统启动自检...</span>
                </div>
                <div className={`flex items-center gap-2 ${
                  diagnosisPhase === 'detecting' || diagnosisPhase === 'analyzing' || diagnosisPhase === 'fixing' || diagnosisPhase === 'resolved'
                    ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {(diagnosisPhase === 'detecting' || diagnosisPhase === 'analyzing' || diagnosisPhase === 'fixing' || diagnosisPhase === 'resolved') ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  <span>日志分析完成 ✓</span>
                </div>
                <div className={`flex items-center gap-2 ${
                  diagnosisPhase === 'analyzing' || diagnosisPhase === 'fixing' || diagnosisPhase === 'resolved'
                    ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {(diagnosisPhase === 'analyzing' || diagnosisPhase === 'fixing' || diagnosisPhase === 'resolved') ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  <span>根因定位: 检索缓存过期</span>
                </div>
                <div className={`flex items-center gap-2 ${
                  diagnosisPhase === 'fixing' || diagnosisPhase === 'resolved'
                    ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {(diagnosisPhase === 'fixing' || diagnosisPhase === 'resolved') ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  <span>执行修复策略...</span>
                </div>
                <div className={`flex items-center gap-2 ${
                  diagnosisPhase === 'resolved' ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {diagnosisPhase === 'resolved' ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  <span>修复完成，验证通过</span>
                </div>
              </div>
            </div>
          </div>

          {/* 可视化 */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-orange-500/20">
            <h4 className="text-lg font-semibold text-white mb-6">异常分布</h4>
            <div className="space-y-4">
              {[
                { type: '幻觉输出', count: 12, severity: 'high' },
                { type: '检索失败', count: 8, severity: 'medium' },
                { type: '超时错误', count: 5, severity: 'low' },
                { type: '配置异常', count: 3, severity: 'medium' },
              ].map((item, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-gray-300">{item.type}</span>
                      <span className="text-sm text-gray-500">{item.count}次</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          item.severity === 'high' ? 'bg-red-500' :
                          item.severity === 'medium' ? 'bg-orange-500' : 'bg-yellow-500'
                        }`}
                        style={{ width: `${(item.count / 15) * 100}%` }}
                      />
                    </div>
                  </div>
                  <AlertTriangle className={`w-5 h-5 ${
                    item.severity === 'high' ? 'text-red-400' :
                    item.severity === 'medium' ? 'text-orange-400' : 'text-yellow-400'
                  }`} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// 版本分叉区域
const ForkingSection = () => {
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null);
  const branches = [
    { id: 'main', name: 'v3-main', type: 'main', commits: 156, status: 'active' },
    { id: 'feature-1', name: 'v4-autonomy', type: 'feature', commits: 23, status: 'active' },
    { id: 'feature-2', name: 'v4-diagnosis', type: 'feature', commits: 18, status: 'active' },
    { id: 'feature-3', name: 'experiment-1', type: 'experiment', commits: 5, status: 'abandoned' },
  ];

  return (
    <section id="forking" className="min-h-screen py-24 px-8 bg-gradient-to-b from-slate-950 to-pink-950/20">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          number="05"
          title="版本分叉引擎"
          subtitle="并行探索多进化路径，智能选择最优分支"
        />

        <div className="grid lg:grid-cols-3 gap-8">
          {/* 分支树可视化 */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
            <h4 className="text-lg font-semibold text-white mb-6">进化分支图谱</h4>

            <div className="relative">
              {/* Git风格分支线 */}
              <svg viewBox="0 0 500 300" className="w-full">
                {/* 主干 */}
                <line x1="50" y1="50" x2="50" y2="280" stroke="#334155" strokeWidth="3" />
                <circle cx="50" cy="50" r="8" fill="#10B981" />
                <circle cx="50" cy="150" r="6" fill="#10B981" />
                <circle cx="50" cy="230" r="6" fill="#10B981" />
                <circle cx="50" cy="280" r="8" fill="#10B981" />

                {/* 功能分支1 */}
                <path d="M50 100 Q150 80 200 120 T300 100" fill="none" stroke="#8B5CF6" strokeWidth="2" strokeDasharray="5,5" />
                <circle cx="200" cy="120" r="6" fill="#8B5CF6" className="cursor-pointer hover:r-8 transition-all" onClick={() => setSelectedBranch('feature-1')} />

                {/* 功能分支2 */}
                <path d="M50 150 Q120 180 180 200 T280 180" fill="none" stroke="#F472B6" strokeWidth="2" strokeDasharray="5,5" />
                <circle cx="180" cy="200" r="6" fill="#F472B6" className="cursor-pointer hover:r-8 transition-all" onClick={() => setSelectedBranch('feature-2')} />

                {/* 已废弃分支 */}
                <path d="M50 80 Q80 60 100 90" fill="none" stroke="#475569" strokeWidth="1" strokeDasharray="3,3" />
                <circle cx="100" cy="90" r="4" fill="#475569" />

                {/* 提交点 */}
                {[...Array(8)].map((_, i) => (
                  <circle
                    key={i}
                    cx={50 + (i % 2) * 10}
                    cy={80 + i * 30}
                    r="3"
                    fill="#475569"
                  />
                ))}
              </svg>

              {/* 图例 */}
              <div className="flex gap-6 mt-4 justify-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-sm text-gray-400">主分支</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span className="text-sm text-gray-400">功能分支</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-pink-500" />
                  <span className="text-sm text-gray-400">实验分支</span>
                </div>
              </div>
            </div>
          </div>

          {/* 分支信息面板 */}
          <div className="space-y-4">
            {branches.map((branch) => (
              <button
                key={branch.id}
                onClick={() => setSelectedBranch(branch.id)}
                className={`w-full p-4 rounded-xl text-left transition-all duration-300 ${
                  selectedBranch === branch.id
                    ? 'bg-pink-500/20 border border-pink-500/50'
                    : 'bg-slate-900/50 border border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`font-medium ${
                    branch.type === 'main' ? 'text-emerald-400' :
                    branch.type === 'feature' ? 'text-purple-400' : 'text-gray-400'
                  }`}>
                    {branch.name}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    branch.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {branch.status === 'active' ? '活跃' : '已废弃'}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>{branch.commits} commits</span>
                  <span>{(branch.commits * 3.2).toFixed(1)} days</span>
                </div>
              </button>
            ))}

            {selectedBranch && (
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 mt-4">
                <h5 className="font-medium text-white mb-2">分支指标</h5>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">性能提升</p>
                    <p className="text-lg font-bold text-green-400">+23%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">错误率</p>
                    <p className="text-lg font-bold text-red-400">-15%</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

// 路线图区域
const RoadmapSection = () => {
  const phases = [
    {
      phase: 'Phase 1',
      title: '基础架构',
      duration: '0-3个月',
      items: ['自诊断模块开发', '合成数据生成器', '代码优化框架', '版本分叉引擎'],
      status: 'current',
    },
    {
      phase: 'Phase 2',
      title: '自主进化',
      duration: '4-9个月',
      items: ['完整进化闭环', '多分支并行探索', '自我测试引擎', '性能基准体系'],
      status: 'upcoming',
    },
    {
      phase: 'Phase 3',
      title: '数字孪生',
      duration: '10-18个月',
      items: ['实体镜像同步', '预测性维护', '自适应优化', '智能资源调度'],
      status: 'upcoming',
    },
    {
      phase: 'Phase 4',
      title: '完全自主',
      duration: '19-24个月',
      items: ['价值对齐传承', '目标自主生成', '持续自我进化', '生态协同'],
      status: 'upcoming',
    },
  ];

  return (
    <section id="roadmap" className="min-h-screen py-24 px-8 bg-slate-950">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          number="06"
          title="演进路线图"
          subtitle="分阶段实现递归自我进化的宏伟目标"
        />

        <div className="relative">
          {/* 时间线 */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-cyan-500 via-purple-500 to-pink-500 hidden md:block" />

          <div className="space-y-8">
            {phases.map((phase, index) => (
              <div key={index} className="relative md:ml-16">
                {/* 时间线点 */}
                <div className={`absolute -left-10 w-6 h-6 rounded-full border-4 border-slate-950 ${
                  phase.status === 'current' ? 'bg-cyan-500 animate-pulse' :
                  phase.status === 'completed' ? 'bg-green-500' : 'bg-slate-700'
                } hidden md:block`} />

                <div className={`p-6 rounded-2xl transition-all duration-300 ${
                  phase.status === 'current'
                    ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30'
                    : 'bg-slate-900/50 border border-slate-800'
                }`}>
                  <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
                    <div>
                      <span className="text-sm text-cyan-400 font-mono">{phase.phase}</span>
                      <h3 className="text-2xl font-bold text-white">{phase.title}</h3>
                    </div>
                    <span className="text-gray-400 text-sm mt-2 md:mt-0">{phase.duration}</span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-3">
                    {phase.items.map((item, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          phase.status === 'current' ? 'bg-cyan-400' :
                          phase.status === 'completed' ? 'bg-green-400' : 'bg-gray-600'
                        }`} />
                        <span className="text-gray-300">{item}</span>
                      </div>
                    ))}
                  </div>

                  {phase.status === 'current' && (
                    <div className="mt-4 pt-4 border-t border-cyan-500/20">
                      <div className="flex items-center gap-2 text-cyan-400 text-sm">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                        正在进行中
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

// 主应用组件
function App() {
  const [activeSection, setActiveSection] = useState('hero');

  useEffect(() => {
    const handleScroll = () => {
      const sections = ['hero', 'overview', 'evolution', 'twin', 'diagnosis', 'forking', 'roadmap'];
      const scrollPosition = window.scrollY + window.innerHeight / 2;

      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const { offsetTop, offsetHeight } = element;
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="bg-slate-950 min-h-screen text-white font-sans">
      <Navigation activeSection={activeSection} setActiveSection={setActiveSection} />
      <HeroSection />
      <OverviewSection />
      <EvolutionSection />
      <TwinSection />
      <DiagnosisSection />
      <ForkingSection />
      <RoadmapSection />

      {/* 页脚 */}
      <footer className="py-12 px-8 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-gray-500 mb-4">
            AI Partner Evolution System — 从工具到伙伴的进化之路
          </p>
          <p className="text-sm text-gray-600">
            基于 v3.0 数字本体论 与 v4.0 递归自我进化架构
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
