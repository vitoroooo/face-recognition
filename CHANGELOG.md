# Changelog - Insta360 Link 2 Face Recognition System

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-06-08

### 🎉 Major Updates
- **Modular Configuration**: Introduced `config.py` for centralized settings management
- **Enhanced Error Handling**: Better error messages and troubleshooting guidance
- **Performance Optimization**: Configurable frame processing and face detection limits
- **Debug Mode**: Real-time debugging information and performance metrics
- **Interactive Controls**: Keyboard shortcuts for runtime configuration

### ✨ New Features
- **FPS Counter**: Real-time FPS display (toggle with 'f' key)
- **Debug Toggle**: Runtime debug mode switching ('d' key)
- **Camera Testing**: New `test_camera.py` script to find available cameras
- **Setup Automation**: Windows batch scripts for easy setup and running
- **Confidence Scoring**: Face recognition confidence display in debug mode
- **Enhanced Visual Feedback**: Better bounding boxes and text rendering

### 🛠️ Improvements
- **Better Database Loading**: More informative face database initialization
- **Camera Info Display**: Shows actual camera resolution and FPS
- **Flexible Naming**: Support for underscores in filenames (converted to spaces)
- **Performance Tuning**: Configurable detection frequency and face processing limits
- **Code Organization**: Separated configuration from main logic

### 📁 New Files
- `config.py` - Centralized configuration file
- `requirements.txt` - Python dependencies list
- `setup_environment.bat` - Automated setup script for Windows
- `run_app.bat` - Easy application launcher for Windows
- `test_camera.py` - Camera testing utility
- `CHANGELOG.md` - This changelog file
- `README.md` - Comprehensive documentation

### 🎮 Keyboard Controls
- `q` - Quit application
- `r` - Reload face database (planned feature)
- `d` - Toggle debug mode
- `f` - Toggle FPS display

### ⚙️ Configuration Options
- Camera index and resolution settings
- Face recognition tolerance and performance tuning
- Visual appearance customization (colors, fonts, etc.)
- Debug and development options

### 🐛 Bug Fixes
- Fixed case sensitivity in file extension detection
- Improved error handling for camera connection issues
- Better handling of empty face database
- More robust face encoding processing

### 🔧 Technical Improvements
- Modular code structure for better maintainability
- Type hints and better documentation
- Consistent error messaging
- Performance monitoring capabilities

---

## [1.0.0] - Initial Release

### ✨ Initial Features
- Real-time face detection using OpenCV
- Face recognition with face_recognition library
- Support for Insta360 Link 2 camera
- Basic visual feedback with bounding boxes
- Local face database from images folder
- Simple console output for status

### 📋 Basic Functionality
- Load face encodings from `faces/` folder
- Real-time video capture and processing
- Face matching with configurable tolerance
- Visual indicators for known/unknown faces

---

## 🔮 Planned Features (Future Releases)

### Version 2.1 (Near Future)
- [ ] Face database reload without restart ('r' key implementation)
- [ ] Multiple face encodings per person for better accuracy
- [ ] Face recognition statistics and logging
- [ ] Configuration GUI for non-technical users
- [ ] Auto-backup of face database

### Version 3.0 (Long Term)
- [ ] Web interface for remote monitoring
- [ ] SQLite database for face data and logs
- [ ] Multiple camera support
- [ ] Cloud sync capabilities
- [ ] Mobile app companion
- [ ] Advanced analytics dashboard
- [ ] Integration with security systems