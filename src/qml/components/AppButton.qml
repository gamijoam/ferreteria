// AppButton.qml - Modern Material Design Button Component
import QtQuick
import QtQuick.Controls
// import "../styles"

Button {
    id: control
    
    // Custom properties
    property string variant: "primary" // primary, secondary, success, danger, warning, outlined, text
    property bool loading: false
    property string iconName: ""
    
    implicitWidth: Math.max(120, contentItem.implicitWidth + leftPadding + rightPadding)
    implicitHeight: 48
    
    leftPadding: 24
    rightPadding: 24
    topPadding: 16
    bottomPadding: 16
    
    font.family: "Segoe UI"
    font.pixelSize: 14
    font.weight: Font.Medium
    
    // Background
    background: Rectangle {
        radius: 8
        
        gradient: Gradient {
            GradientStop { 
                position: 0.0
                color: {
                    if (!control.enabled) return "#64748b"
                    switch(control.variant) {
                        case "primary": return "#2196F3"
                        case "secondary": return "#8b5cf6"
                        case "success": return "#4CAF50"
                        case "danger": return "#F44336"
                        case "warning": return "#FF9800"
                        case "outlined": return "transparent"
                        case "text": return "transparent"
                        default: return "#2196F3"
                    }
                }
            }
            GradientStop { 
                position: 1.0
                color: {
                    if (!control.enabled) return "#64748b"
                    switch(control.variant) {
                        case "primary": return "#1976D2"
                        case "secondary": return "#7c3aed"
                        case "success": return "#388E3C"
                        case "danger": return "#D32F2F"
                        case "warning": return "#F57C00"
                        case "outlined": return "transparent"
                        case "text": return "transparent"
                        default: return "#1976D2"
                    }
                }
            }
        }
        
        border.width: control.variant === "outlined" ? 2 : 0
        border.color: control.variant === "outlined" ? "#2196F3" : "transparent"
        
        // Hover overlay
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: "white"
            opacity: control.hovered ? 0.1 : 0
            
            Behavior on opacity {
                NumberAnimation { duration: 150 }
            }
        }
        
        // Pressed overlay
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: "black"
            opacity: control.pressed ? 0.2 : 0
            
            Behavior on opacity {
                NumberAnimation { duration: 150 }
            }
        }
        
        // Ripple effect
        Rectangle {
            id: ripple
            anchors.centerIn: parent
            width: 0
            height: width
            radius: width / 2
            color: "white"
            opacity: 0
            
            ParallelAnimation {
                id: rippleAnimation
                NumberAnimation {
                    target: ripple
                    property: "width"
                    from: 0
                    to: control.width * 2
                    duration: 600
                    easing.type: Easing.OutCubic
                }
                NumberAnimation {
                    target: ripple
                    property: "opacity"
                    from: 0.5
                    to: 0
                    duration: 600
                    easing.type: Easing.OutCubic
                }
            }
        }
        
        // Shadow - Removed ShaderEffect for compatibility
        // layer.enabled: control.variant !== "text" && control.variant !== "outlined"
        // layer.effect: ShaderEffect { ... }
    }
    
    // Content
    contentItem: Row {
        spacing: 8
        
        // Loading spinner
        Rectangle {
            visible: control.loading
            width: 20
            height: 20
            radius: 10
            color: "transparent"
            border.width: 2
            border.color: control.variant === "outlined" || control.variant === "text" 
                          ? "#2196F3" : "white"
            
            Rectangle {
                width: 6
                height: 6
                radius: 3
                color: parent.border.color
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 2
            }
            
            RotationAnimation on rotation {
                running: control.loading
                loops: Animation.Infinite
                from: 0
                to: 360
                duration: 1000
            }
        }
        
        // Icon (placeholder - you can integrate FontAwesome or custom icons)
        Text {
            visible: control.iconName !== "" && !control.loading
            text: control.iconName
            font: control.font
            color: control.variant === "outlined" || control.variant === "text" 
                   ? "#2196F3" : "white"
            verticalAlignment: Text.AlignVCenter
        }
        
        // Text
        Text {
            text: control.text
            font: control.font
            color: {
                if (!control.enabled) return "#64748b"
                if (control.variant === "outlined" || control.variant === "text") 
                    return "#2196F3"
                return "white"
            }
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    // Animations
    Behavior on scale {
        NumberAnimation { duration: 150 }
    }
    
    // Mouse handling for ripple
    onPressed: {
        rippleAnimation.start()
    }
    
    // Cursor
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onPressed: (mouse) => { mouse.accepted = false }
    }
}
