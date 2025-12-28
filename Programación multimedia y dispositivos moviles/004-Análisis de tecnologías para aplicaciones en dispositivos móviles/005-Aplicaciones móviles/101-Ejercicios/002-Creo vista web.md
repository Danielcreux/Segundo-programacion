1.-Arrastro Webview:

2.-Le  pongo id: mivistaweb

3.-Codigo resultante de la vista:
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Button"
        tools:layout_editor_absoluteX="160dp"
        tools:layout_editor_absoluteY="787dp" />

    <WebView
        android:id="@+id/mivistaweb"
        android:layout_width="409dp"
        android:layout_height="729dp"
        android:layout_marginStart="1dp"
        android:layout_marginTop="1dp"
        android:layout_marginEnd="1dp"
        android:layout_marginBottom="1dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>

Nuevo controlador:

package com.jocarsa.aplicacionweb2

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

class MainActivity : AppCompatActivity() {

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        // Mantener el comportamiento de bordes del template
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        // Referencia al WebView definido en tu XML
        val webView = findViewById<WebView>(R.id.mivistaweb)

        // Para que los enlaces se abran dentro del WebView y no en el navegador externo
        webView.webViewClient = WebViewClient()

        // Muchas webs modernas necesitan JavaScript
        val settings = webView.settings
        settings.javaScriptEnabled = true

        // Cargar la página
        webView.loadUrl("https://jocarsa.com")
    }

    // Opcional pero recomendable: botón atrás navega en el historial del WebView
    override fun onBackPressed() {
        val webView = findViewById<WebView>(R.id.mivistaweb)
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
