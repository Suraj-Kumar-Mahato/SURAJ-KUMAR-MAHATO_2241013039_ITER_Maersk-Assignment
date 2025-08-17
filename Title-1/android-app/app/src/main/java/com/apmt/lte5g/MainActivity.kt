package com.apmt.lte5g

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.os.Build
import android.os.Bundle
import android.telephony.*
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import java.time.Instant
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var fusedClient: FusedLocationProviderClient
    private lateinit var telephonyManager: TelephonyManager

    private lateinit var statusText: TextView
    private lateinit var metricsText: TextView
    private lateinit var sendButton: Button

    private var lastLocation: Location? = null
    private var lastPayload: Map<String, Any?> = emptyMap()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        metricsText = findViewById(R.id.metricsText)
        sendButton = findViewById(R.id.sendButton)

        fusedClient = LocationServices.getFusedLocationProviderClient(this)
        telephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager

        sendButton.setOnClickListener {
            ApiClient.postMeasurement(this, lastPayload) { ok, msg ->
                runOnUiThread {
                    statusText.text = if (ok) "Sent ✓" else "Send failed: $msg"
                }
            }
        }

        ensurePermissions()
    }

    private fun ensurePermissions() {
        val needed = mutableListOf<String>()
        val perms = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.READ_PHONE_STATE
        )
        for (p in perms) {
            if (ContextCompat.checkSelfPermission(this, p) != PackageManager.PERMISSION_GRANTED) {
                needed.add(p)
            }
        }
        if (needed.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, needed.toTypedArray(), 1)
        } else {
            startCollecting()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 1) startCollecting()
    }

    @SuppressLint("MissingPermission")
    private fun startCollecting() {
        // Location
        fusedClient.lastLocation.addOnSuccessListener { loc ->
            lastLocation = loc
        }

        // Telephony signal listener
        val listener = object : PhoneStateListener() {
            override fun onSignalStrengthsChanged(signalStrength: SignalStrength?) {
                super.onSignalStrengthsChanged(signalStrength)
                updatePayload(signalStrength)
            }
            override fun onCellInfoChanged(cellInfo: MutableList<CellInfo>?) {
                super.onCellInfoChanged(cellInfo)
                updatePayload(telephonyManager.signalStrength)
            }
        }
        @Suppress("DEPRECATION")
        telephonyManager.listen(listener, PhoneStateListener.LISTEN_SIGNAL_STRENGTHS or PhoneStateListener.LISTEN_CELL_INFO)
    }

    @SuppressLint("MissingPermission")
    private fun updatePayload(signalStrength: SignalStrength?) {
        val subInfo = telephonyManager.subscriptionId
        val simOp = telephonyManager.simOperator
        val mcc = if (simOp?.length ?: 0 >= 3) simOp?.substring(0,3) else null
        val mnc = if (simOp?.length ?: 0 > 3) simOp?.substring(3) else null

        val cells = telephonyManager.allCellInfo
        var rsrp: Double? = null
        var rsrq: Double? = null
        var sinr: Double? = null
        var tech = "Unknown"
        var pci: String? = null
        var earfcn: String? = null
        var nrarfcn: String? = null
        var tac: String? = null
        var eci: String? = null

        if (cells != null) {
            for (c in cells) {
                if (c.isRegistered) {
                    when (c) {
                        is CellInfoLte -> {
                            tech = "LTE"
                            val s = c.cellSignalStrength
                            rsrp = s.rsrp.toDouble()
                            rsrq = s.rsrq.toDouble()
                            pci = c.cellIdentity.pci.toString()
                            earfcn = c.cellIdentity.earfcn?.toString()
                            tac = c.cellIdentity.tac?.toString()
                            eci = c.cellIdentity.ci?.toString()
                        }
                        is CellInfoNr -> {
                            tech = "NR"
                            val s = c.cellSignalStrength as? CellSignalStrengthNr
                            if (s != null) {
                                // Some vendors report UNAVAILABLE as Integer.MAX_VALUE; guard
                                rsrp = s.ssRsrp.takeIf { it < 140 }?.toDouble()?.let { -it }
                                rsrq = s.ssRsrq.takeIf { it < 20 }?.toDouble()?.let { -it }
                                sinr = s.ssSinr.toDouble()
                            }
                            val id = c.cellIdentity as? CellIdentityNr
                            if (id != null) {
                                nrarfcn = id.nrarfcn?.toString()
                                pci = id.pci?.toString()
                                tac = id.tac?.toString()
                                eci = id.nci?.toString()
                            }
                        }
                    }
                    break
                }
            }
        }

        val loc = lastLocation
        val deviceHash = ApiClient.hashId("${Build.MANUFACTURER}-${Build.MODEL}")
        val payload = mutableMapOf<String, Any?>(
            "ts" to Instant.now().toString(),
            "device_hash" to deviceHash,
            "tech" to tech,
            "mcc" to mcc,
            "mnc" to mnc,
            "tac" to tac,
            "eci" to eci,
            "pci" to pci,
            "earfcn" to earfcn,
            "nrarfcn" to nrarfcn,
            "rsrp" to rsrp,
            "rsrq" to rsrq,
            "sinr" to sinr,
            "rssi" to null,
            "bandwidth" to null,
            "lat" to (loc?.latitude ?: 19.0760),
            "lon" to (loc?.longitude ?: 72.8777),
            "extra" to mapOf("model" to Build.MODEL, "sdk" to Build.VERSION.SDK_INT)
        )

        lastPayload = payload
        metricsText.text = payload.entries.joinToString("\n") { "${it.key}: ${it.value}" }
        statusText.text = "Ready to send"
    }
}
