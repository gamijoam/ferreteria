// Card.qml - Glassmorphic Card Component
import QtQuick
import QtQuick.Effects
import "../styles"

Rectangle {
    id: card
    
    // Custom properties
    property int elevation: 2
    property bool hoverable: true
    property bool clickable: false
    property alias contentItem: contentContainer
    
    signal clicked()
    
    radius: Theme.radiusLg
    color: Qt.rgba(30/255, 41/255, 59/255, 0.7) // Semi-transparent surface
    border.width: 1
    border.color: Qt.rgba(255, 255, 255, 0.1)
    
    // Glassmorphism backdrop blur effect
    layer.enabled: true
    layer.effect: MultiEffect {
        blurEnabled: true
        blur: 0.5
        blurMax: 32
        blurMultiplier: 0.5
    }
    
    // Content container
    Item {
        id: contentContainer
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
    }
    
    // Hover effect
    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: "white"
        opacity: card.hoverable && mouseArea.containsMouse ? 0.05 : 0
        
        Behavior on opacity {
            NumberAnimation { duration: Theme.transitionNormal }
        }
    }
    
    // Shadow
    Rectangle {
        anchors.fill: parent
        anchors.margins: -elevation
        radius: parent.radius
        color: "transparent"
        border.width: 0
        z: -1
        
        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowBlur: elevation * 4
            shadowOpacity: 0.3
            shadowColor: "black"
        }
    }
    
    // Mouse area for interactions
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: card.hoverable
        cursorShape: card.clickable ? Qt.PointingHandCursor : Qt.ArrowCursor
        
        onClicked: {
            if (card.clickable) {
                card.clicked()
            }
        }
    }
    
    // Scale animation on hover
    scale: card.hoverable && mouseArea.containsMouse ? 1.02 : 1.0
    
    Behavior on scale {
        NumberAnimation { 
            duration: Theme.transitionNormal
            easing.type: Easing.OutCubic
        }
    }
    
    // Transform origin for scaling
    transformOrigin: Item.Center
}
