// AppButton.qml - Modern Material Design Button Component
import QtQuick
import QtQuick.Controls
import "../styles"

Button {
    id: control
    
    // Custom properties
    property string variant: "primary" // primary, secondary, success, danger, warning, outlined, text
    property bool loading: false
    property string iconName: ""
    
    implicitWidth: Math.max(120, contentItem.implicitWidth + leftPadding + rightPadding)
    implicitHeight: 48
    
    leftPadding: Theme.spacingLg
    rightPadding: Theme.spacingLg
    topPadding: Theme.spacingMd
    bottomPadding: Theme.spacingMd
    
    font.family: Theme.fontFamily
    font.pixelSize: Theme.fontSizeMd
    font.weight: Theme.fontWeightMedium
    
    // Background
    background: Rectangle {
        radius: Theme.radiusMd
        
        gradient: Gradient {
            GradientStop { 
                position: 0.0
                color: {
                    if (!control.enabled) return Theme.textDisabled
                    switch(control.variant) {
                        case "primary": return Theme.primary
                        case "secondary": return Theme.secondary
                        case "success": return Theme.success
                        case "danger": return Theme.danger
                        case "warning": return Theme.warning
                        case "outlined": return "transparent"
                        case "text": return "transparent"
                        default: return Theme.primary
                    }
                }
            }
            GradientStop { 
                position: 1.0
                color: {
                    if (!control.enabled) return Theme.textDisabled
                    switch(control.variant) {
                        case "primary": return Theme.primaryDark
                        case "secondary": return Theme.secondaryDark
                        case "success": return Theme.successDark
                        case "danger": return Theme.dangerDark
                        case "warning": return Theme.warningDark
                        case "outlined": return "transparent"
                        case "text": return "transparent"
                        default: return Theme.primaryDark
                    }
                }
            }
        }
        
        border.width: control.variant === "outlined" ? 2 : 0
        border.color: control.variant === "outlined" ? Theme.primary : "transparent"
        
        // Hover overlay
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: "white"
            opacity: control.hovered ? 0.1 : 0
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.transitionFast }
            }
        }
        
        // Pressed overlay
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: "black"
            opacity: control.pressed ? 0.2 : 0
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.transitionFast }
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
        
        // Shadow
        layer.enabled: control.variant !== "text" && control.variant !== "outlined"
        layer.effect: ShaderEffect {
            property color shadowColor: Qt.rgba(0, 0, 0, 0.3)
            fragmentShader: "
                varying highp vec2 qt_TexCoord0;
                uniform lowp sampler2D source;
                uniform lowp vec4 shadowColor;
                void main() {
                    lowp vec4 tex = texture2D(source, qt_TexCoord0);
                    gl_FragColor = mix(shadowColor, tex, tex.a);
                }
            "
        }
    }
    
    // Content
    contentItem: Row {
        spacing: Theme.spacingSm
        
        // Loading spinner
        Rectangle {
            visible: control.loading
            width: 20
            height: 20
            radius: 10
            color: "transparent"
            border.width: 2
            border.color: control.variant === "outlined" || control.variant === "text" 
                          ? Theme.primary : "white"
            
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
                   ? Theme.primary : "white"
            verticalAlignment: Text.AlignVCenter
        }
        
        // Text
        Text {
            text: control.text
            font: control.font
            color: {
                if (!control.enabled) return Theme.textDisabled
                if (control.variant === "outlined" || control.variant === "text") 
                    return Theme.primary
                return "white"
            }
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    // Animations
    Behavior on scale {
        NumberAnimation { duration: Theme.transitionFast }
    }
    
    // Mouse handling for ripple
    onPressed: {
        rippleAnimation.start()
    }
    
    // Cursor
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onPressed: mouse.accepted = false
    }
}
