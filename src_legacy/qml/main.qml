// main.qml - Root Application Window
import QtQuick
import QtQuick.Controls
import QtQuick.Window

ApplicationWindow {
    id: root
    visible: true
    width: 1200
    height: 700
    minimumWidth: 1000
    minimumHeight: 600
    title: "POS Ultra - Sistema de Gestión"
    
    // Stack view for navigation
    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: "views/LoginView.qml"
        
        // Page transitions
        pushEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 250
            }
            PropertyAnimation {
                property: "x"
                from: root.width
                to: 0
                duration: 250
                easing.type: Easing.OutCubic
            }
        }
        
        pushExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to: 0
                duration: 250
            }
        }
        
        popEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 250
            }
        }
        
        popExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to: 0
                duration: 250
            }
            PropertyAnimation {
                property: "x"
                from: 0
                to: root.width
                duration: 250
                easing.type: Easing.OutCubic
            }
        }
    }
}
