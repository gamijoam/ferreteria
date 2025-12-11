// LoginView.qml - Modern Login Screen
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: loginView
    anchors.fill: parent
    
    // Gradient background
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#0f2027" }
        GradientStop { position: 0.5; color: "#203a43" }
        GradientStop { position: 1.0; color: "#2c5364" }
    }
    
    // Main container
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        // LEFT PANEL - Branding
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.4
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#2196F3" }
                GradientStop { position: 1.0; color: "#1976D2" }
            }
            
            ColumnLayout {
                anchors.centerIn: parent
                width: parent.width * 0.8
                spacing: 32
                
                // Logo
                Image {
                    id: logoImage
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 180
                    Layout.preferredHeight: 180
                    fillMode: Image.PreserveAspectFit
                    source: authBridge.logoPath !== "" ? "file:///" + authBridge.logoPath : ""
                    visible: authBridge.logoPath !== ""
                }
                
                // Business Name
                Text {
                    id: brandTitle
                    Layout.alignment: Qt.AlignHCenter
                    text: authBridge.businessName
                    font.family: "Segoe UI"
                    font.pixelSize: 36
                    font.weight: Font.Bold
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                }
                
                // Tagline
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Sistema de Gestión Empresarial"
                    font.family: "Segoe UI"
                    font.pixelSize: 16
                    color: Qt.rgba(1, 1, 1, 0.9)
                    horizontalAlignment: Text.AlignHCenter
                }
                
                // Spacer
                Item { Layout.preferredHeight: 32 }
                
                // Features
                Column {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 16
                    
                    Repeater {
                        model: [
                            "Control de Inventario",
                            "Punto de Venta",
                            "Reportes en Tiempo Real",
                            "Gestion de Clientes"
                        ]
                        
                        Text {
                            text: "✓ " + modelData
                            font.family: "Segoe UI"
                            font.pixelSize: 14
                            color: Qt.rgba(1, 1, 1, 0.85)
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
        }
        
        // RIGHT PANEL - Login Form
        Rectangle {
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: "white"
            
            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(parent.width * 0.7, 400)
                spacing: 24
                
                // Welcome Text
                Text {
                    text: "Bienvenido"
                    font.family: "Segoe UI"
                    font.pixelSize: 30
                    font.weight: Font.Bold
                    color: "#2c3e50"
                }
                
                Text {
                    text: "Ingrese sus credenciales para continuar"
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    color: "#7f8c8d"
                }
                
                Item { Layout.preferredHeight: 16 }
                
                // Username Field
                Column {
                    Layout.fillWidth: true
                    spacing: 8
                    
                    Text {
                        text: "Usuario"
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        font.weight: Font.Medium
                        color: "#2c3e50"
                    }
                    
                    TextField {
                        id: usernameField
                        width: parent.width
                        placeholderText: "Ingrese su usuario"
                        font.family: "Segoe UI"
                        font.pixelSize: 14
                        
                        background: Rectangle {
                            radius: 8
                            color: "#f5f5f5"
                            border.width: usernameField.activeFocus ? 2 : 1
                            border.color: usernameField.activeFocus ? "#2196F3" : "#e0e0e0"
                        }
                        
                        Keys.onReturnPressed: passwordField.forceActiveFocus()
                    }
                }
                
                // Password Field
                Column {
                    Layout.fillWidth: true
                    spacing: 8
                    
                    Text {
                        text: "Contraseña"
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        font.weight: Font.Medium
                        color: "#2c3e50"
                    }
                    
                    TextField {
                        id: passwordField
                        width: parent.width
                        placeholderText: "Ingrese su contraseña"
                        echoMode: TextInput.Password
                        font.family: "Segoe UI"
                        font.pixelSize: 14
                        
                        background: Rectangle {
                            radius: 8
                            color: "#f5f5f5"
                            border.width: passwordField.activeFocus ? 2 : 1
                            border.color: errorMessage.visible ? "#F44336" : (passwordField.activeFocus ? "#2196F3" : "#e0e0e0")
                        }
                        
                        Keys.onReturnPressed: loginButton.clicked()
                    }
                }
                
                // Error Message
                Text {
                    id: errorMessage
                    Layout.fillWidth: true
                    visible: false
                    text: ""
                    font.family: "Segoe UI"
                    font.pixelSize: 12
                    color: "#F44336"
                    wrapMode: Text.WordWrap
                }
                
                Item { Layout.preferredHeight: 8 }
                
                // Login Button
                Button {
                    id: loginButton
                    Layout.fillWidth: true
                    text: "INICIAR SESIÓN"
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    font.weight: Font.Medium
                    
                    contentItem: Text {
                        text: loginButton.text
                        font: loginButton.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    background: Rectangle {
                        radius: 8
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#2196F3" }
                            GradientStop { position: 1.0; color: "#1976D2" }
                        }
                        opacity: loginButton.pressed ? 0.8 : (loginButton.hovered ? 0.95 : 1.0)
                    }
                    
                    onClicked: {
                        errorMessage.visible = false
                        
                        if (usernameField.text === "" || passwordField.text === "") {
                            errorMessage.text = "Por favor complete todos los campos"
                            errorMessage.visible = true
                            return
                        }
                        
                        authBridge.login(usernameField.text, passwordField.text)
                    }
                }
                
                Item { Layout.fillHeight: true }
                
                // Version
                Text {
                    Layout.alignment: Qt.AlignRight
                    text: "v2.0"
                    font.family: "Segoe UI"
                    font.pixelSize: 10
                    color: "#bdc3c7"
                }
            }
        }
    }
    
    // Connections to AuthBridge
    Connections {
        target: authBridge
        
        function onLoginSuccess(username, role) {
            // Navigate to main window
            stackView.push("MainView.qml", {
                "username": username,
                "role": role
            })
        }
        
        function onLoginFailed(error) {
            errorMessage.text = error
            errorMessage.visible = true
            passwordField.text = ""
            passwordField.forceActiveFocus()
        }
    }
    
    // Auto-focus username on load
    Component.onCompleted: {
        usernameField.forceActiveFocus()
    }
}
