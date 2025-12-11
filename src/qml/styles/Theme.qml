// Theme.qml - Material Design 3 Theme Configuration
pragma Singleton
import QtQuick

QtObject {
    // ===== PRIMARY COLORS =====
    readonly property color primary: "#2196F3"
    readonly property color primaryDark: "#1976D2"
    readonly property color primaryLight: "#E3F2FD"
    readonly property color primaryContainer: "#BBDEFB"
    
    // ===== SECONDARY COLORS =====
    readonly property color secondary: "#8b5cf6"
    readonly property color secondaryDark: "#7c3aed"
    readonly property color secondaryLight: "#ddd6fe"
    
    // ===== ACCENT COLORS =====
    readonly property color accent: "#06b6d4"
    readonly property color accentDark: "#0891b2"
    
    // ===== SEMANTIC COLORS =====
    readonly property color success: "#4CAF50"
    readonly property color successDark: "#388E3C"
    readonly property color successLight: "#C8E6C9"
    
    readonly property color warning: "#FF9800"
    readonly property color warningDark: "#F57C00"
    readonly property color warningLight: "#FFE0B2"
    
    readonly property color danger: "#F44336"
    readonly property color dangerDark: "#D32F2F"
    readonly property color dangerLight: "#FFCDD2"
    
    readonly property color info: "#00BCD4"
    readonly property color infoDark: "#0097A7"
    readonly property color infoLight: "#B2EBF2"
    
    // ===== NEUTRAL COLORS =====
    readonly property color background: "#0f172a"
    readonly property color backgroundLight: "#1e293b"
    readonly property color surface: "#1e293b"
    readonly property color surfaceVariant: "#334155"
    
    readonly property color textPrimary: "#f8fafc"
    readonly property color textSecondary: "#94a3b8"
    readonly property color textDisabled: "#64748b"
    
    readonly property color border: "#334155"
    readonly property color borderLight: "#475569"
    readonly property color divider: "#1e293b"
    
    // ===== OVERLAY COLORS =====
    readonly property color overlay: "#000000"
    readonly property real overlayOpacity: 0.5
    
    readonly property color scrim: "#000000"
    readonly property real scrimOpacity: 0.32
    
    // ===== GRADIENTS =====
    function primaryGradient() {
        return Qt.createQmlObject('import QtQuick; Gradient {
            GradientStop { position: 0.0; color: "#3b82f6" }
            GradientStop { position: 1.0; color: "#8b5cf6" }
        }', this)
    }
    
    function successGradient() {
        return Qt.createQmlObject('import QtQuick; Gradient {
            GradientStop { position: 0.0; color: "#4CAF50" }
            GradientStop { position: 1.0; color: "#388E3C" }
        }', this)
    }
    
    function dangerGradient() {
        return Qt.createQmlObject('import QtQuick; Gradient {
            GradientStop { position: 0.0; color: "#F44336" }
            GradientStop { position: 1.0; color: "#D32F2F" }
        }', this)
    }
    
    // ===== SPACING =====
    readonly property int spacingXs: 4
    readonly property int spacingSm: 8
    readonly property int spacingMd: 16
    readonly property int spacingLg: 24
    readonly property int spacingXl: 32
    readonly property int spacingXxl: 48
    
    // ===== BORDER RADIUS =====
    readonly property int radiusXs: 4
    readonly property int radiusSm: 6
    readonly property int radiusMd: 8
    readonly property int radiusLg: 12
    readonly property int radiusXl: 16
    readonly property int radiusFull: 9999
    
    // ===== ELEVATION / SHADOWS =====
    readonly property int elevation0: 0
    readonly property int elevation1: 2
    readonly property int elevation2: 4
    readonly property int elevation3: 8
    readonly property int elevation4: 16
    readonly property int elevation5: 24
    
    // ===== TYPOGRAPHY =====
    readonly property string fontFamily: "Inter, Segoe UI, Arial, sans-serif"
    
    readonly property int fontSizeXs: 10
    readonly property int fontSizeSm: 12
    readonly property int fontSizeMd: 14
    readonly property int fontSizeLg: 16
    readonly property int fontSizeXl: 20
    readonly property int fontSize2xl: 24
    readonly property int fontSize3xl: 30
    readonly property int fontSize4xl: 36
    readonly property int fontSize5xl: 48
    
    readonly property int fontWeightNormal: 400
    readonly property int fontWeightMedium: 500
    readonly property int fontWeightSemibold: 600
    readonly property int fontWeightBold: 700
    readonly property int fontWeightExtrabold: 800
    
    // ===== TRANSITIONS =====
    readonly property int transitionFast: 150
    readonly property int transitionNormal: 250
    readonly property int transitionSlow: 350
    
    // ===== Z-INDEX =====
    readonly property int zIndexDropdown: 1000
    readonly property int zIndexSticky: 1020
    readonly property int zIndexFixed: 1030
    readonly property int zIndexModal: 1040
    readonly property int zIndexPopover: 1050
    readonly property int zIndexTooltip: 1060
}
