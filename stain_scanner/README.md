# Stain Scanner

A powerful Flutter mobile application for identifying stains and providing instant removal recommendations.

## 📋 Features

### Core Features
- **📸 Stain Detection**: Capture or upload photos of stains for instant analysis
- **📚 Comprehensive Stain Library**: Browse 8+ common stain types with detailed information
- **🧹 Removal Guides**: Step-by-step instructions for removing detected stains
- **📜 Detection History**: Keep track of all scanned stains with timestamps
- **🎯 Difficulty Ratings**: Easy-to-understand difficulty levels for each stain type

### Supported Stain Types
1. **Coffee/Tea** - Beverage stains
2. **Wine** - Red and white wine stains
3. **Blood** - Fresh and dried blood stains
4. **Grass** - Grass and plant stains
5. **Oil/Grease** - Cooking oils and motor oil
6. **Ink/Pen** - Ink marks and pen stains
7. **Chocolate** - Chocolate and cocoa stains
8. **Makeup** - Foundation and cosmetic stains

## 🏗️ Project Structure

```
lib/
├── main.dart                          # Application entry point
├── models/
│   └── stain.dart                    # Stain data model with database
├── providers/
│   └── stain_provider.dart           # State management using Provider
├── services/
│   └── image_analysis_service.dart   # Image analysis and stain detection
└── screens/
    ├── home_screen.dart              # Main dashboard
    ├── camera_screen.dart            # Camera interface
    ├── stain_details_screen.dart      # Detailed information
    ├── analysis_result_screen.dart    # Results display
    ├── history_screen.dart           # History viewer
    └── stain_library_screen.dart      # Database browser
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK: ^3.11.5
- Dart SDK: Latest stable

### Installation

1. Navigate to project:
```bash
cd stain_scanner
```

2. Install dependencies:
```bash
flutter pub get
```

3. Run the app:
```bash
flutter run
```

## 📦 Key Dependencies

- **provider**: State management
- **camera**: Photo capture
- **image_picker**: Image selection
- **google_fonts**: Typography
- **shared_preferences**: Data persistence
- **image**: Image processing

## 🎨 Screens

- **Home**: Dashboard with quick actions
- **Camera**: Image capture interface
- **Stain Details**: Complete removal instructions
- **History**: Detection history tracker
- **Library**: Searchable stain database

## 💾 Data Persistence

Detection history is automatically saved using SharedPreferences and can be cleared anytime.

## 🔮 Future Enhancements

- Real ML model integration
- Community stain database
- Before/after comparison
- Cloud sync
- Dark mode
- Multi-language support

---

**Built with Flutter 🚀**
