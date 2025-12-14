// AppTextField.qml - Modern Material Design Text Input
import QtQuick
import QtQuick.Controls

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
    // signal textChanged() - Removed to avoid conflict with alias
    
    implicitWidth: 300
    implicitHeight: 72
    
    // Label
    Text {
        id: labelText
        visible: root.label !== ""
        text: root.label
        font.family: "Segoe UI"
        font.pixelSize: 12
        font.weight: Font.Medium
        color: textField.activeFocus ? "#2196F3" : "#666"
        anchors.bottom: inputContainer.top
        anchors.bottomMargin: 8
        anchors.left: parent.left
        
        Behavior on color {
            ColorAnimation { duration: 150 }
        }
    }
    
    // Input container
    Rectangle {
        id: inputContainer
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: root.label !== "" ? labelText.bottom : parent.top
        anchors.topMargin: root.label !== "" ? 8 : 0
        height: 48
        
        radius: 8
        color: "white"
        border.width: 2
        border.color: {
            if (root.hasError) return "#F44336"
            if (textField.activeFocus) return "#2196F3"
            return "#e0e0e0"
        }
        
        Behavior on border.color {
            ColorAnimation { duration: 150 }
        }
        
        Row {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            spacing: 8
            
            // Left icon
            Text {
                visible: root.iconLeft !== ""
                text: root.iconLeft
                font.family: "Segoe UI"
                font.pixelSize: 16
                color: "#666"
                verticalAlignment: Text.AlignVCenter
                anchors.verticalCenter: parent.verticalCenter
            }
            
            // Text input
            TextInput {
                id: textField
                width: parent.width - (root.iconLeft !== "" ? 30 : 0) - (root.iconRight !== "" ? 30 : 0)
                height: parent.height
                
                font.family: "Segoe UI"
                font.pixelSize: 14
                color: "black" 
                selectionColor: "#2196F3"
                selectedTextColor: "white"
                verticalAlignment: TextInput.AlignVCenter
                clip: true
                
                echoMode: root.isPassword ? TextInput.Password : TextInput.Normal
                
                onAccepted: root.accepted()
                // onTextChanged handling is automatic via alias
                
                // Placeholder
                Text {
                    id: placeholder
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    font: textField.font
                    color: "#64748b"
                    visible: textField.text === "" && !textField.activeFocus
                    elide: Text.ElideRight
                }
            }
            
            // Right icon
            Text {
                visible: root.iconRight !== ""
                text: root.iconRight
                font.family: "Segoe UI"
                font.pixelSize: 16
                color: "#666"
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
            color: "#2196F3"
            
            scale: textField.activeFocus ? 1 : 0
            transformOrigin: Item.Center
            
            Behavior on scale {
                NumberAnimation { 
                    duration: 250
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
        font.family: "Segoe UI"
        font.pixelSize: 10
        color: "#F44336"
        anchors.top: inputContainer.bottom
        anchors.topMargin: 4
        anchors.left: parent.left
    }
}
