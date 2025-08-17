package com.apmt.lte5g

import android.content.Context
import okhttp3.*
import java.io.File
import java.io.IOException
import java.security.MessageDigest

object ApiClient {
    // IMPORTANT: Set to your backend URL. For Android emulator to host: http://10.0.2.2:5000
    private const val BASE_URL = "http://10.0.2.2:5000"
    private const val API_KEY = "devkey" // optional; set same value on backend

    private val client = OkHttpClient()

    fun hashId(input: String, salt: String = "android-salt"): String {
        val md = MessageDigest.getInstance("SHA-256")
        val bytes = md.digest((salt + input).toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }
    }

    fun postMeasurement(context: Context, payload: Map<String, Any?>, cb: (Boolean, String?) -> Unit) {
        val json = toJson(payload)
        val req = Request.Builder()
            .url("$BASE_URL/api/v1/measurements")
            .post(RequestBody.create(MediaType.parse("application/json"), json))
            .apply {
                if (API_KEY.isNotEmpty()) header("X-API-KEY", API_KEY)
            }
            .build()

        client.newCall(req).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                queueToDisk(context, json)
                cb(false, e.message)
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    cb(true, null)
                    flushQueue(context)
                } else {
                    queueToDisk(context, json)
                    cb(false, "HTTP ${response.code()}")
                }
            }
        })
    }

    private fun queueToDisk(context: Context, json: String) {
        val dir = File(context.filesDir, "queue")
        dir.mkdirs()
        val f = File(dir, System.currentTimeMillis().toString() + ".json")
        f.writeText(json)
    }

    private fun flushQueue(context: Context) {
        val dir = File(context.filesDir, "queue")
        if (!dir.exists()) return
        dir.listFiles()?.sortedBy { it.name }?.forEach { file ->
            val body = RequestBody.create(MediaType.parse("application/json"), file.readText())
            val req = Request.Builder()
                .url("$BASE_URL/api/v1/measurements")
                .post(body)
                .apply { if (API_KEY.isNotEmpty()) header("X-API-KEY", API_KEY) }
                .build()
            try {
                val resp = client.newCall(req).execute()
                if (resp.isSuccessful) file.delete()
            } catch (_: Exception) { /* keep for later */ }
        }
    }

    private fun toJson(map: Map<String, Any?>): String {
        val sb = StringBuilder("{")
        val iter = map.entries.iterator()
        while (iter.hasNext()) {
            val (k, v) = iter.next()
            sb.append('"').append(k).append('"').append(':')
            sb.append(serialize(v))
            if (iter.hasNext()) sb.append(',')
        }
        sb.append('}')
        return sb.toString()
    }

    private fun serialize(v: Any?): String {
        return when (v) {
            null -> "null"
            is Number, is Boolean -> v.toString()
            is String -> """ + v.replace(""", "\"") + """
            is Map<*, *> -> {
                val entries = v.entries.map { (k, vv) ->
                    ""${k}"" + ":" + serialize(vv)
                }
                "{" + entries.joinToString(",") + "}"
            }
            is Iterable<*> -> {
                val arr = v.map { serialize(it) }
                "[" + arr.joinToString(",") + "]"
            }
            else -> """ + v.toString().replace(""", "\"") + """
        }
    }
}
