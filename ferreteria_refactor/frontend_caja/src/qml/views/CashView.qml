// CashView.qml - Gestión de Caja
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Rectangle {
    id: cashView
    color: "#f5f5f5"
    
    // -- STATE --
    property string sessionStatus: "CLOSED"
    property int sessionId: 0
    property string sessionStart: ""
    property double initialUsd: 0
    property double initialBs: 0
    property double salesTotal: 0
    property double expensesUsd: 0
    property double expensesBs: 0
    property double depositsUsd: 0
    property double depositsBs: 0
    property double expectedUsd: 0
    property double expectedBs: 0
    
    ListModel { id: historyModel }
    
    // -- CONNECTIONS --
    Connections {
        target: cashBridge
        
        function onSessionUpdated(data) {
            sessionStatus = data.status
            if (data.status === "OPEN") {
                sessionId = data.id
                sessionStart = data.start_time
                initialUsd = data.initial_usd
                initialBs = data.initial_bs
                salesTotal = data.sales_total
                expensesUsd = data.expenses_usd
                expensesBs = data.expenses_bs
                depositsUsd = data.deposits_usd
                depositsBs = data.deposits_bs
                expectedUsd = data.expected_usd
                expectedBs = data.expected_bs
            } else {
                // Reset if closed
                sessionId = 0
                sessionStart = ""
                initialUsd = 0
                initialBs = 0
                salesTotal = 0
                expectedUsd = 0
                expectedBs = 0
            }
        }
        
        function onMessage(type, text) {
            if (type === "success") {
                msgLabel.text = text
                successDialog.open()
            } else {
                errMsgLabel.text = text
                errorDialog.open()
            }
        }
        
        function onHistoryLoaded(data) {
            historyModel.clear()
            for (var i = 0; i < data.length; i++) {
                historyModel.append(data[i])
            }
        }
    }
    
    Component.onCompleted: {
        console.log("CashView: Component loaded")
        try {
            cashBridge.getCurrentSession()
            console.log("CashView: getCurrentSession called")
        } catch(e) {
            console.error("CashView Error calling bridge:", e)
        }
    }
    
    // -- UI --
    
    // Header
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 60
        color: "#2196F3"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 16
            
            Text {
                text: "💰 GESTIÓN DE CAJA"
                font.family: "Segoe UI"
                font.pixelSize: 16
                font.weight: Font.Bold
                color: "white"
            }
            
            Item { Layout.fillWidth: true }
            
            AppButton {
                text: "← Volver"
                variant: "outlined"
                onClicked: stackView.pop()
                implicitHeight: 36
                
                background: Rectangle {
                    color: parent.pressed ? Qt.darker("#2196F3", 1.2) : "transparent"
                    radius: 4
                    border.width: 1
                    border.color: "white"
                }
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    // Tabs
    ColumnLayout {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 16
        
        TabBar {
            id: bar
            width: parent.width
            Layout.fillWidth: true
            
            TabButton {
                text: "OPERACIONES DIARIAS"
                width: implicitWidth + 20
            }
            TabButton {
                text: "HISTORIAL DE CIERRES"
                width: implicitWidth + 20
            }
            
            onCurrentIndexChanged: {
                if (currentIndex === 1) {
                    cashBridge.loadHistory()
                } else {
                    cashBridge.getCurrentSession()
                }
            }
        }
        
        StackLayout {
            width: parent.width
            currentIndex: bar.currentIndex
            Layout.fillHeight: true
            
            // --- TAB 1: OPERACIONES ---
            Rectangle {
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                // Content Switcher based on Session Status
                Loader {
                    anchors.fill: parent
                    sourceComponent: sessionStatus === "OPEN" ? activeSessionComponent : openSessionComponent
                }
            }
            
            // --- TAB 2: HISTORIAL ---
            Rectangle {
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10
                    
                    Text {
                        text: "Historial de Sesiones Cerradas"
                        font.bold: true
                        font.pixelSize: 16
                    }
                    
                    Button {
                        text: "Actualizar"
                        onClicked: cashBridge.loadHistory()
                    }
                    
                    // Header
                    RowLayout {
                        spacing: 0
                        height: 40
                        Repeater {
                            model: ["ID", "Fecha Cierre", "Usuario", "Inicial (USD/Bs)", "Esperado", "Real", "Diferencia"]
                            delegate: Rectangle {
                                width: index === 0 ? 50 : (index === 1 ? 150 : 120)
                                Layout.fillWidth: index === 3 || index === 4 || index === 5 || index === 6
                                height: 40
                                color: "#f0f0f0"
                                border.color: "#ddd"
                                Text { anchors.centerIn: parent; text: modelData; font.bold: true }
                            }
                        }
                    }
                    
                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: historyModel
                        clip: true
                        
                        delegate: Rectangle {
                            width: parent.width
                            height: 40
                            color: index % 2 === 0 ? "white" : "#f9f9f9"
                            
                            RowLayout {
                                anchors.fill: parent
                                spacing: 0
                                
                                Text { text: model.id; width: 50; horizontalAlignment: Text.AlignHCenter }
                                Text { text: model.end_time; width: 150; horizontalAlignment: Text.AlignHCenter }
                                Text { text: model.user; width: 120; horizontalAlignment: Text.AlignHCenter }
                                Text { text: model.initial; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                Text { text: model.expected; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                Text { text: model.reported; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 24
                                    color: (Math.abs(model.diff_usd) < 0.01 && Math.abs(model.diff_bs) < 0.01) ? "#C8E6C9" : "#FFCDD2"
                                    radius: 4
                                    Text { 
                                        anchors.centerIn: parent
                                        text: "$" + model.diff_usd.toFixed(2) + " / Bs" + model.diff_bs.toFixed(2)
                                        font.bold: true
                                        color: (Math.abs(model.diff_usd) < 0.01 && Math.abs(model.diff_bs) < 0.01) ? "#2E7D32" : "#C62828"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // -- COMPONENTS --
    
    Component {
        id: openSessionComponent
        ColumnLayout {
            anchors.centerIn: parent
            width: 400
            spacing: 20
            
            Text {
                text: "🔒 LA CAJA ESTÁ CERRADA"
                font.bold: true
                font.pixelSize: 18
                color: "#666"
                Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: "Ingrese el fondo inicial para abrir turno:"
                Layout.alignment: Qt.AlignHCenter
            }
            
            GridLayout {
                columns: 2
                rowSpacing: 10
                columnSpacing: 10
                
                Text { text: "Fondo USD:" }
                SpinBox {
                    id: startUsd
                    from: 0
                    to: 100000000
                    value: 0
                    editable: true
                    stepSize: 100 // x100 for decimals workaround logic or just standard integer
                    // SpinBox is integer only usually. Need workaround or just use textfield or specialized DoubleSpinBox if available (PySide6 QML uses QtQuick.Controls SpinBox which is integer)
                    // Simplified: We assume integer for now or use workaround. 
                    // Better: use AppTextField for logic.
                }
                
                Text { text: "Fondo Bs:" }
                SpinBox {
                    id: startBs
                    from: 0
                    to: 100000000
                    value: 0
                    editable: true
                }
            }
            // Replacing SpinBox with AppTextField for simpler decimal input
            
            ColumnLayout {
                spacing: 5
                Text { text: "Fondo USD ($):" }
                AppTextField { 
                    id: inputStartUsd; 
                    text: "0.00"; 
                    Layout.fillWidth: true
                }
            }
             ColumnLayout {
                spacing: 5
                Text { text: "Fondo Bs (Bs):" }
                AppTextField { 
                    id: inputStartBs; 
                    text: "0.00"; 
                    Layout.fillWidth: true 
                }
            }
            
            AppButton {
                text: "🔓 ABRIR CAJA"
                variant: "success"
                Layout.fillWidth: true
                onClicked: {
                    cashBridge.openSession(parseFloat(inputStartUsd.text), parseFloat(inputStartBs.text))
                }
            }
        }
    }
    
    Component {
        id: activeSessionComponent
        ColumnLayout {
            spacing: 20
            anchors.margins: 30
            
            // Info Header
            Rectangle {
                Layout.fillWidth: true
                height: 80
                color: "#E3F2FD" // Light Blue
                radius: 8
                border.color: "#2196F3"
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    
                    ColumnLayout {
                        Text { text: "SESIÓN ACTIVA"; font.bold: true; color: "#1565C0" }
                        Text { text: "Inicio: " + sessionStart }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    AppButton {
                        text: "CERRAR CAJA"
                        variant: "danger"
                        onClicked: closeDialog.open()
                    }
                }
            }
            
            // Metrics Cards
            RowLayout {
                Layout.fillWidth: true
                spacing: 20
                
                // USD Card
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    color: "#E8F5E9"
                    radius: 8
                    border.color: "#4CAF50"
                    
                    ColumnLayout {
                        anchors.centerIn: parent
                        Text { text: "Saldo Esperado USD"; color: "#2E7D32" }
                        Text { 
                            text: "$" + expectedUsd.toFixed(2)
                            font.pixelSize: 24
                            font.bold: true
                            color: "#2E7D32" 
                        }
                        Text { text: "Ventas: $" + salesTotal.toFixed(2); font.pixelSize: 12 }
                    }
                }
                
                // Bs Card
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    color: "#FFF3E0"
                    radius: 8
                    border.color: "#FF9800"
                    
                    ColumnLayout {
                        anchors.centerIn: parent
                        Text { text: "Saldo Esperado Bs"; color: "#EF6C00" }
                        Text { 
                            text: "Bs " + expectedBs.toFixed(2)
                            font.pixelSize: 24
                            font.bold: true
                            color: "#EF6C00" 
                        }
                    }
                }
            }
            
            // Actions
            GroupBox {
                title: "Acciones Rapidas"
                Layout.fillWidth: true
                
                RowLayout {
                    spacing: 20
                    AppButton {
                        text: "➖ Registrar Gasto / Retiro"
                        variant: "warning"
                        onClicked: expenseDialog.open()
                    }
                    
                    AppButton {
                        text: "➕ Ingreso Extra"
                        variant: "secondary"
                        onClicked: console.log("To Implement Deposit")
                    }
                }
            }
            
            Item { Layout.fillHeight: true }
        }
    }
    
    // -- DIALOGS --
    
    Dialog {
        id: expenseDialog
        title: "Registrar Gasto"
        width: 400
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 15
            
            Text { text: "Monto del Gasto:" }
            RowLayout {
                AppTextField { id: expAmount; placeholderText: "0.00"; Layout.fillWidth: true }
                ComboBox {
                    id: expCurrency
                    model: ["USD", "Bs"]
                }
            }
            
            Text { text: "Descripción / Motivo:" }
            AppTextField { id: expDesc; placeholderText: "Ej. Pago limpieza"; Layout.fillWidth: true }
        }
        
        onAccepted: {
            if (expAmount.text && expDesc.text) {
                cashBridge.addMovement("EXPENSE", parseFloat(expAmount.text), expCurrency.currentText, expDesc.text)
                expAmount.text = ""
                expDesc.text = ""
            }
        }
    }
    
    Dialog {
        id: closeDialog
        title: "Cierre de Caja (Ciego)"
        width: 400
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 15
            
            Text { 
                text: "Por favor cuente el dinero físico en caja e ingréselo a continuación." 
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            Text { text: "Efectivo USD Contado:" }
            AppTextField { id: closeUsd; text: "0.00"; Layout.fillWidth: true }
            
            Text { text: "Efectivo Bs Contado:" }
            AppTextField { id: closeBs; text: "0.00"; Layout.fillWidth: true }
        }
        
        onAccepted: {
            cashBridge.closeSession(parseFloat(closeUsd.text), parseFloat(closeBs.text))
            closeUsd.text = "0.00"
            closeBs.text = "0.00"
        }
    }

    Dialog {
        id: successDialog
        title: "Éxito"
        width: 400
        modal: true
        standardButtons: Dialog.Ok
        
        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width
            Text { 
                id: msgLabel
                property alias text: msgLabel.text
                font.family: "Consolas" // Monospace for alignment
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }
        }
    }
    
    Dialog {
        id: errorDialog
        title: "Error"
        width: 300
        modal: true
        standardButtons: Dialog.Ok
        Text { id: errMsgLabel; property alias text: errMsgLabel.text; color: "red"; wrapMode: Text.WordWrap }
    }
}
