# Contributing to ParrotWinKernel

Thank you for your interest in contributing to ParrotWinKernel! This document provides guidelines for contributing to this revolutionary project.

## 📜 Important: Legal Notice

This is proprietary software. By contributing, you agree that:
1. You have the legal right to contribute the code
2. Your contributions will be subject to the project's proprietary license
3. The project maintainer retains all rights to the contributed code

Please review the [LICENSE](LICENSE) file before contributing.

## 🎯 Areas for Contribution

We welcome contributions in the following areas:

### High Priority
- **Windows API Implementations** - Implement missing ntoskrnl.exe APIs
- **Hardware Driver Testing** - Test with real Windows drivers
- **Port Forwarding Features** - Enhance network port forwarding capabilities
- **AI Model Improvements** - Optimize the tiny AI engine
- **Bug Fixes** - Fix issues reported in GitHub Issues

### Medium Priority
- **Documentation** - Improve or add documentation
- **Performance Optimization** - Make things faster
- **Test Coverage** - Add unit and integration tests
- **Example Drivers** - Create example Windows drivers for testing

### Low Priority
- **Code Style** - Improve code formatting and style
- **Build System** - Enhance build scripts
- **Packaging** - Create packages for different distros

## 🔧 Development Setup

### Prerequisites
```bash
# Ubuntu/Debian
sudo apt-get install build-essential linux-headers-$(uname -r) \
    python3 python3-pip git curl libjson-c-dev libcurl4-openssl-dev

# Fedora/RHEL
sudo dnf install gcc make kernel-devel python3 python3-pip git curl \
    json-c-devel libcurl-devel
```

### Clone and Build
```bash
git clone https://github.com/jameshroop-art/P-A-rrot-SecW-I-n.git
cd P-A-rrot-SecW-I-n
./scripts/build.sh
```

### Running Tests
```bash
./scripts/run_tests.sh
```

## 📝 Contribution Process

### 1. Fork and Clone
```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/P-A-rrot-SecW-I-n.git
cd P-A-rrot-SecW-I-n
git remote add upstream https://github.com/jameshroop-art/P-A-rrot-SecW-I-n.git
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes
- Follow the existing code style
- Add comments for complex logic
- Update documentation if needed
- Add tests for new features

### 4. Test Your Changes
```bash
# Build
make clean && make

# Run tests
./scripts/run_tests.sh

# Test specific component
make -C tests/unit test
```

### 5. Commit
```bash
git add .
git commit -m "feat: add port forwarding for NDIS drivers"
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build system, dependencies, etc.

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 🎨 Code Style

### C Code
- Use Linux kernel coding style for kernel modules
- Use consistent indentation (4 spaces or tabs as per file)
- Function names: `snake_case`
- Constants: `UPPER_CASE`
- Structs: `snake_case_t`

```c
// Good
int wck_device_create(struct wck_device *device) {
    if (!device) {
        return -EINVAL;
    }
    
    // Implementation
    return 0;
}

// Bad
int WCKDeviceCreate(struct wck_device* device){
    if(!device)
        return -EINVAL;
    return 0;
}
```

### Python Code
- Follow PEP 8
- Use type hints
- Add docstrings

```python
def train_model(data: np.ndarray, labels: np.ndarray) -> tf.keras.Model:
    """Train the tiny AI model.
    
    Args:
        data: Training data array
        labels: Training labels
        
    Returns:
        Trained Keras model
    """
    # Implementation
    pass
```

## 🧪 Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Aim for >80% code coverage

### Integration Tests
- Test component interactions
- Use real kernel module (in VM if needed)
- Test with sample drivers

### Test File Naming
```
tests/
├── unit/
│   ├── test_pe_loader.c
│   ├── test_ntoskrnl_io.c
│   └── test_tiny_ai.c
└── integration/
    ├── test_driver_loading.c
    └── test_port_forwarding.c
```

## 📚 Documentation

### Code Comments
```c
/**
 * wck_device_create - Create a Windows-compatible device object
 * @name: Device name (e.g., "\\Device\\MyDevice")
 * @type: Device type (FILE_DEVICE_XXX)
 * @device_out: Output pointer for created device
 *
 * Creates a DEVICE_OBJECT structure compatible with Windows drivers.
 * The device is registered with the kernel and can receive IRPs.
 *
 * Return: 0 on success, negative error code on failure
 */
int wck_device_create(const char *name, uint32_t type, 
                      struct wck_device **device_out);
```

### Markdown Documentation
- Use clear headings
- Include code examples
- Add diagrams where helpful
- Keep language simple and clear

## 🐛 Bug Reports

When reporting bugs, include:
1. **Description** - What happened?
2. **Expected Behavior** - What should happen?
3. **Steps to Reproduce** - How to reproduce?
4. **Environment** - OS, kernel version, hardware
5. **Logs** - Relevant log output
6. **Screenshots** - If applicable

## 💡 Feature Requests

When requesting features, include:
1. **Problem** - What problem does this solve?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other possible solutions?
4. **Use Cases** - Real-world scenarios?

## 🔍 Code Review Process

All contributions go through code review:
1. **Automated Checks** - CI runs tests and linters
2. **Security Scan** - CodeQL checks for vulnerabilities
3. **Manual Review** - Maintainers review the code
4. **Discussion** - Questions and suggestions
5. **Approval** - Once approved, PR is merged

## 🎯 Priority Labels

PRs and issues are labeled by priority:
- `P0: Critical` - Security issues, crashes, data loss
- `P1: High` - Major features, important bugs
- `P2: Medium` - Minor features, minor bugs
- `P3: Low` - Nice-to-have, cosmetic changes

## ✅ Definition of Done

A contribution is "done" when:
- [ ] Code is written and follows style guide
- [ ] Tests are added and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Code review approved
- [ ] CI/CD pipeline passes
- [ ] Merged to main branch

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

## 📧 Questions?

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Email**: For private/security issues

## 🎉 Thank You!

Every contribution, big or small, helps make ParrotWinKernel better. Thank you for being part of this revolutionary project!

---

**Remember**: This project is pushing the boundaries of what's possible. Your contributions are helping make history! 🚀
