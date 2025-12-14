import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: pinAuthDialog
    title: "Autorización Requerida"
    modal: true
    width: 400
    height: 320
    anchors.centerIn: parent
    
    property string actionDescription: "realizar esta acción"
    property bool authorized: false
    property string authorizedUser: ""
    property string authorizedRole: ""
    
    signal authGranted(string username, string role)
    signal authDenied()
    
    function resetFields() {
        usernameField.text = ""
        pinField.text = ""
        errorLabel.text = ""
        authorized = false
        authorizedUser = ""
        authorizedRole = ""
    }
    
    function requestAuthorization(action) {
        actionDescription = action
        resetFields()
        open()
        usernameField.forceActiveFocus()
    }
    
    onOpened: {
        usernameField.forceActiveFocus()
    }
    
    Connections {
        target: pinAuthBridge
        
        function onAuthSuccess(username, role) {
            authorized = true
            authorizedUser = username
            authorizedRole = role
            authGranted(username, role)
            pinAuthDialog.accept()
        }
        
        function onAuthFailed(errorMsg) {
            errorLabel.text = errorMsg
            errorLabel.color = "#D32F2F"
            pinField.text = ""
            pinField.forceActiveFocus()
        }
    }
    
    contentItem: Rectangle {
        color: "white"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16
            
            // Title
            Text {
                Layout.fillWidth: true
                text: "Se requiere autorización para " + actionDescription
                font.family: "Segoe UI"
                font.pixelSize: 13
                font.weight: Font.Bold
                color: "#D32F2F"
                wrapMode: Text.WordWrap
            }
            
            // Username
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                
                Text {
                    text: "Usuario:"
                    font.family: "Segoe UI"
                    font.pixelSize: 12
                    color: "#333"
                }
                
                TextField {
                    id: usernameField
                    Layout.fillWidth: true
                    placeholderText: "Ingrese su usuario"
                    font.family: "Segoe UI"
                    font.pixelSize: 13
                    
                    background: Rectangle {
                        color: "#f9f9f9"
                        radius: 4
                        border.width: parent.activeFocus ? 2 : 1
                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                    }
                    
                    Keys.onReturnPressed: pinField.forceActiveFocus()
                }
            }
            
            // PIN
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                
                Text {
                    text: "PIN:"
                    font.family: "Segoe UI"
                    font.pixelSize: 12
                    color: "#333"
                }
                
                TextField {
                    id: pinField
                    Layout.fillWidth: true
                    placeholderText: "Ingrese su PIN"
                    echoMode: TextInput.Password
                    maximumLength: 6
                    font.family: "Segoe UI"
                    font.pixelSize: 13
                    
                    background: Rectangle {
                        color: "#f9f9f9"
                        radius: 4
                        border.width: parent.activeFocus ? 2 : 1
                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                    }
                    
                    Keys.onReturnPressed: validateAndAuthorize()
                }
            }
            
            // Info label
            Text {
                Layout.fillWidth: true
                text: "Solo usuarios autorizados (Admin/Manager) pueden aprobar esta acción"
                font.family: "Segoe UI"
                font.pixelSize: 10
                font.italic: true
                color: "#666"
                wrapMode: Text.WordWrap
            }
            
            // Error label
            Text {
                id: errorLabel
                Layout.fillWidth: true
                text: ""
                font.family: "Segoe UI"
                font.pixelSize: 11
                font.weight: Font.Bold
                color: "#D32F2F"
                wrapMode: Text.WordWrap
                visible: text !== ""
            }
            
            Item { Layout.fillHeight: true }
            
            // Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Cancelar"
                    Layout.preferredWidth: 100
                    
                    background: Rectangle {
                        color: parent.pressed ? "#BDBDBD" : (parent.hovered ? "#E0E0E0" : "#F5F5F5")
                        radius: 4
                        border.width: 1
                        border.color: "#BDBDBD"
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "#333"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        authorizationDenied()
                        pinAuthDialog.reject()
                    }
                }
                
                Button {
                    text: "Autorizar"
                    Layout.preferredWidth: 100
                    
                    background: Rectangle {
                        color: parent.pressed ? "#388E3C" : (parent.hovered ? "#43A047" : "#4CAF50")
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: validateAndAuthorize()
                }
            }
        }
    }
    
    function validateAndAuthorize() {
        var username = usernameField.text.trim()
        var pin = pinField.text.trim()
        
        if (!username || !pin) {
            errorLabel.text = "Debe ingresar usuario y PIN"
            return
        }
        
        errorLabel.text = ""
        pinAuthBridge.validatePIN(username, pin, actionDescription)
    }
}
