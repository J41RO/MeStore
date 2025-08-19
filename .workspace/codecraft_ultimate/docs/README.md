# 📚 CodeCraft Ultimate v6.0 Documentation

Welcome to the comprehensive documentation for CodeCraft Ultimate v6.0 - the advanced AI-human collaborative development tool.

## 📖 Table of Contents

- [Quick Start Guide](quick-start.md)
- [Installation](installation.md)
- [Core Concepts](core-concepts.md)
- [Operations Reference](operations/)
  - [Surgical Operations](operations/surgical.md)
  - [Analysis Operations](operations/analysis.md)
  - [Generation Operations](operations/generation.md)
  - [Refactoring Operations](operations/refactoring.md)
  - [Debugging Operations](operations/debugging.md)
  - [Optimization Operations](operations/optimization.md)
- [AI Integration](ai-integration.md)
- [Plugin Development](plugin-development.md)
- [Configuration](configuration.md)
- [Examples](../examples/)
- [API Reference](api/)

## 🚀 What's New in v6.0

CodeCraft Ultimate v6.0 represents a complete evolution from the surgical modifier tool into a comprehensive development platform:

### ✨ Enhanced Features

- **6 Operation Categories**: Surgical, Analysis, Generation, Refactoring, Debugging, Optimization
- **AI-First Design**: Structured JSON output optimized for AI consumption
- **Plugin Architecture**: Extensible system for custom operations
- **Universal Language Support**: Python, JavaScript, TypeScript, Java, C++, C#, and more
- **Intelligent Context Management**: Project-aware suggestions and recommendations
- **Advanced Analysis**: Complexity metrics, security scanning, dependency analysis

### 🔄 Migration from v5.3

If you're upgrading from the Surgical Modifier Ultimate v5.3:

1. All existing surgical operations are supported with enhanced features
2. New command structure: `codecraft surgical <operation>` for surgical ops
3. Backward compatibility maintained for basic operations
4. Enhanced output format with AI-optimized JSON structure

## 🎯 Core Philosophy

CodeCraft Ultimate is built around three core principles:

1. **AI-Human Collaboration**: Seamless integration between AI analysis and human execution
2. **Intelligent Automation**: Smart suggestions and context-aware operations
3. **Universal Compatibility**: Support for any programming language and framework

## 📋 Quick Command Reference

```bash
# Surgical Operations (Enhanced from v5.3)
codecraft create src/app.py "print('Hello World')"
codecraft replace src/app.py "Hello World" "Hello CodeCraft"
codecraft extract-method src/app.py 10 25 "process_data"

# Analysis Operations
codecraft analyze-complexity src/ --format=detailed
codecraft security-scan . --severity=high
codecraft project-health .

# Generation Operations
codecraft generate-component react UserProfile --framework=react
codecraft generate-tests src/utils.py --test-framework=pytest
codecraft scaffold-project web my-app

# AI-Optimized Output
codecraft analyze-complexity src/ --output-format=json
```

## 🤖 AI Integration

CodeCraft Ultimate is specifically designed for AI-human collaborative workflows:

### Structured Output
All operations return structured JSON with:
- Operation results and status
- File context and dependencies
- Intelligent next-step suggestions
- Error details and recommendations

### Collaborative Workflow
1. AI analyzes task and generates CodeCraft command
2. Human executes command in terminal
3. CodeCraft returns structured results with context
4. AI interprets results and suggests next steps
5. Cycle continues until task completion

## 🔧 Getting Started

1. **Install**: `pip install -e .`
2. **Basic Usage**: `codecraft --help`
3. **First Command**: `codecraft analyze-complexity .`
4. **AI Integration**: Use `--output-format=json` for AI consumption

## 📞 Support & Community

- **Documentation**: Complete guides and API reference
- **Examples**: Real-world usage scenarios
- **Issues**: Report bugs and request features
- **Discussions**: Community support and best practices

---

**CodeCraft Ultimate v6.0** - *Empowering the future of AI-human collaborative development* 🚀✨