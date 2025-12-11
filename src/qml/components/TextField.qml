// TextField.qml - Modern Material Design Text Input
import QtQuick
import QtQuick.Controls
import "../styles"

Item {
    id: root
    
    // Custom properties
    property alias text: textField.text
    property alias placeholderText: placeholder.text
    property string label: ""
    property bool isPassword: false
    property bool hasError: false
    property string errorText: ""
    property string iconLeft: ""
    property string iconRight: ""
    property alias readOnly: textField.readOnly
    
    signal accepted()
    signal textChanged()
    
    implicitWidth: 300
    implicitHeight: 72
    
    // Label
    Text {
        id: labelText
        visible: root.label !== ""
        text: root.label
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSm
        font.weight: Theme.fontWeightMedium
        color: textField.activeFocus ? Theme.primary : Theme.textSecondary
        anchors.bottom: inputContainer.top
        anchors.bottomMargin: Theme.spacingSm
        anchors.left: parent.left
        
        Behavior on color {
            ColorAnimation { duration: Theme.transitionFast }
        }
    }
    
    // Input container
    Rectangle {
        id: inputContainer
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: root.label !== "" ? labelText.bottom : parent.top
        anchors.topMargin: root.label !== "" ? Theme.spacingSm : 0
        height: 48
        
        radius: Theme.radiusMd
        color: Theme.surface
        border.width: 2
        border.color: {
            if (root.hasError) return Theme.danger
            if (textField.activeFocus) return Theme.primary
            return Theme.border
        }
        
        Behavior on border.color {
            ColorAnimation { duration: Theme.transitionFast }
        }
        
        Row {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingMd
            anchors.rightMargin: Theme.spacingMd
            spacing: Theme.spacingSm
            
            // Left icon
            Text {
                visible: root.iconLeft !== ""
                text: root.iconLeft
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeLg
                color: Theme.textSecondary
                verticalAlignment: Text.AlignVCenter
                anchors.verticalCenter: parent.verticalCenter
            }
            
            // Text input
            TextInput {
                id: textField
                width: parent.width - (root.iconLeft !== "" ? 30 : 0) - (root.iconRight !== "" ? 30 : 0)
                height: parent.height
                
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeMd
                color: Theme.textPrimary
                selectionColor: Theme.primary
                selectedTextColor: "white"
                verticalAlignment: TextInput.AlignVCenter
                
                echoMode: root.isPassword ? TextInput.Password : TextInput.Normal
                
                onAccepted: root.accepted()
                onTextChanged: root.textChanged()
                
                // Placeholder
                Text {
                    id: placeholder
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    font: textField.font
                    color: Theme.textDisabled
                    visible: textField.text === "" && !textField.activeFocus
                }
            }
            
            // Right icon
            Text {
                visible: root.iconRight !== ""
                text: root.iconRight
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeLg
                color: Theme.textSecondary
                verticalAlignment: Text.AlignVCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }
        
        // Focus underline animation
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 2
            color: Theme.primary
            
            scale: textField.activeFocus ? 1 : 0
            transformOrigin: Item.Center
            
            Behavior on scale {
                NumberAnimation { 
                    duration: Theme.transitionNormal
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
    
    // Error text
    Text {
        id: errorLabel
        visible: root.hasError && root.errorText !== ""
        text: root.errorText
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        color: Theme.danger
        anchors.top: inputContainer.bottom
        anchors.topMargin: Theme.spacingXs
        anchors.left: parent.left
    }
}
