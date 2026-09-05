package com.onepaper.domain.backup

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class WebDavPathTest {
    @Test
    fun defaultRemoteIsZip() {
        assertTrue(WebDavPath.DEFAULT_REMOTE.endsWith(".zip"))
    }

    @Test
    fun joinsHttpsBaseAndPath() {
        val url = WebDavPath.resolve("https://dav.jianguoyun.com/dav/", "onepaper/onepaper-backup.json")
        assertEquals("https://dav.jianguoyun.com/dav/onepaper/onepaper-backup.json", url)
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsCleartext() {
        WebDavPath.requireHttps("http://example.com/dav")
    }

    @Test
    fun parentCollectionStopsAtFolder() {
        val parent = WebDavPath.parentCollection("https://dav.example/dav/onepaper/onepaper-backup.json")
        assertEquals("https://dav.example/dav/onepaper", parent)
        assertNull(WebDavPath.parentCollection("https://dav.example"))
    }
}
