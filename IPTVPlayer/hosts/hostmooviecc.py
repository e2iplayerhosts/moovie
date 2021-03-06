# -*- coding: utf-8 -*-
###################################################
# 2019-07-11 by Alec - modified Mooviecc
###################################################
HOST_VERSION = "1.4"
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, byteify, GetTmpDir, GetIPTVPlayerVerstion, MergeDicts
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
###################################################

###################################################
# FOREIGN import
###################################################
import urlparse
import re
import urllib
import random
import os
import datetime
import time
import zlib
import cookielib
import base64
import traceback
from copy import deepcopy
try:
    import json
except Exception:
    import simplejson as json
from Components.config import config, ConfigText, ConfigYesNo, getConfigListEntry
from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS
from datetime import datetime
from hashlib import sha1
###################################################

###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvmultipleinputbox import IPTVMultipleInputBox
from Screens.MessageBox import MessageBox
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.mooviecc_id = ConfigYesNo(default = False)
config.plugins.iptvplayer.boxtipus = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.boxrendszer = ConfigText(default = "", fixed_size = False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry("id:", config.plugins.iptvplayer.mooviecc_id))
    return optionList
###################################################

def gettytul():
    return 'https://moovie.cc/'

class MoovieCC(CBaseHostClass):
 
    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'moovie.cc', 'cookie':'moovie.cc.cookie'})
        self.DEFAULT_ICON_URL = 'https://moovie.cc/images/logo.png'
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        self.HEADER = {'User-Agent': self.USER_AGENT, 'DNT':'1', 'Accept': 'text/html'}
        self.AJAX_HEADER = dict(self.HEADER)
        self.AJAX_HEADER.update( {'X-Requested-With': 'XMLHttpRequest'} )
        self.MAIN_URL = 'https://moovie.cc/'
        self.vivn = GetIPTVPlayerVerstion()
        self.porv = self.gits()
        self.pbtp = '-'
        self.btps = config.plugins.iptvplayer.boxtipus.value
        self.brdr = config.plugins.iptvplayer.boxrendszer.value
        self.aid = config.plugins.iptvplayer.mooviecc_id.value
        self.aid_ki = ''
        self.ilk = False
        self.cacheLinks    = {}
        self.cacheSortOrder = []
        self.defaultParams = {'header':self.HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
                            
        self.MOVIES_CAT_TAB = [{'category':'movies_cats', 'title': _('Categories'), 'url':self.getFullUrl('/online-filmek/'), 'desc':'', 'tps':'1'},
                               #{'category':'list_main', 'title': 'Premier filmek', 'tab_id':'prem_movies', 'desc':''},
                               {'category':'list_main', 'title': 'Népszerű online filmek', 'tab_id':'pop_movies', 'desc':'', 'tps':'1' }
                              ]
        
        self.SERIES_CAT_TAB = [{'category':'series_cats', 'title': _('Categories'), 'url':self.getFullUrl('/online-sorozatok/'), 'desc':'', 'tps':'2'},
                               {'category':'list_main', 'title': 'Népszerű online sorozatok', 'tab_id':'pop_series', 'desc':'', 'tps':'2'},
                               {'category':'list_main', 'title': 'Új Epizódok', 'tab_id':'new_episodes', 'desc':'', 'tps':'2'}
                              ]
        
    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        
        def _getFullUrl(url):
            if self.cm.isValidUrl(url):
                return url
            else:
                return urlparse.urljoin(baseUrl, url)
            
        addParams['cloudflare_params'] = {'domain':self.up.getDomain(baseUrl), 'cookie_file':self.COOKIE_FILE, 'User-Agent':self.USER_AGENT, 'full_url_handle':_getFullUrl}
        sts, data = self.cm.getPageCFProtection(baseUrl, addParams, post_data)
        return sts, data
        
    def listMainMenu(self, cItem):
        try:
            self.cacheLinks = {}
            if not self.ebbtit(): return
            if self.btps != '' and self.brdr != '': self.pbtp = self.btps.strip() + ' - ' + self.brdr.strip()
            tab_movies = 'mooviecc_filmek'
            desc_movies = self.getdvdsz(tab_movies, 'Filmek megjelenítése...')
            tab_series = 'mooviecc_sorozatok'
            desc_series = self.getdvdsz(tab_series, 'Sorozatok megjelenítése...')
            tab_now_watched = 'mooviecc_most_nezik'
            desc_now_watched = self.getdvdsz(tab_now_watched, 'Épp most nézik...')
            tab_best_rated = 'mooviecc_legjobbak'
            desc_best_rated = self.getdvdsz(tab_best_rated, 'Legjobbra értékeltek megjelenítése...')
            tab_ajanlott = 'mooviecc_ajanlott'
            desc_ajanlott = self.getdvdsz(tab_ajanlott, 'Ajánlott, nézett tartalmak megjelenítése...')
            tab_keresett = 'mooviecc_keresett_tartalom'
            desc_keresett = self.getdvdsz(tab_keresett, 'Keresett tartalmak megjelenítése...')
            tab_search = 'mooviecc_kereses'
            desc_search = self.getdvdsz(tab_search, 'Keresés...')
            tab_search_hist = 'mooviecc_kereses_elozmeny'
            desc_search_hist = self.getdvdsz(tab_search_hist, 'Keresés az előzmények között...')
            MAIN_CAT_TAB = [{'category':'list_movies', 'title': _('Movies'), 'tps':'1', 'cat_tab_id':tab_movies, 'desc':desc_movies },
                            {'category':'list_series', 'title': _('Series'), 'tps':'2', 'cat_tab_id':tab_series, 'desc':desc_series },
                            {'category':'list_main', 'title': 'Legjobbra értékelt', 'tps':'0', 'cat_tab_id':tab_best_rated, 'tab_id':'now_watched', 'desc':desc_best_rated },
                            {'category':'list_main', 'title': 'Épp most nézik', 'tps':'0', 'cat_tab_id':tab_now_watched, 'tab_id':'best_rated', 'desc':desc_now_watched },
                            {'category':'list_uj', 'title': 'Ajánlott, nézett tartalmak', 'cat_tab_id':tab_ajanlott, 'desc':desc_ajanlott},
                            {'category':'list_uj', 'title': 'Keresett tartalmak', 'cat_tab_id':tab_keresett, 'desc':desc_keresett},
                            {'category':'search', 'title': _('Search'), 'search_item':True, 'tps':'0', 'cat_tab_id':tab_search, 'desc':desc_search },
                            {'category':'search_history', 'title': _('Search history'), 'tps':'0', 'cat_tab_id':tab_search_hist, 'desc':desc_search_hist } 
                           ]               
            self.listsTab(MAIN_CAT_TAB, {'name':'category'})
            vtb = self.malvadnav(cItem, '6', '4', '0')
            if len(vtb) > 0:
                for item in vtb:
                    item['category'] = 'list_third'
                    self.addVideo(item)
            self.ilk = True
        except Exception:
            printExc()
        
    def listMainItems(self, cItem, nextCategory):
        me = '</ul></ul>'
        m1 = '<li'
        m2 = '</li>'
        
        tabID = cItem.get('tab_id', '')
        if tabID == 'prem_movies':
            ms = 'Premier filmek'
        elif tabID == 'best_rated':
            ms = 'Épp most nézik'
        elif tabID == 'pop_series':
            ms = 'Népszerű online sorozatok'
        elif tabID == 'new_episodes':
            ms = 'Új Epizódok'
            me = '</table>'
            m1 = '<tr'
            m2 = '</tr>'
        elif tabID == 'now_watched':
            ms = 'Még több jó film »'
        elif tabID == 'pop_movies':
            ms = 'Még több népszerű film »'
        else: return
        
        sts, data = self.getPage(self.getMainUrl())
        if not sts: return
        
        data = self.cm.ph.getDataBeetwenMarkers(data, ms, '</ul></ul>')[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, m1, m2)
        for item in data:
            url = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''')[0] )
            if not self.cm.isValidUrl(url): continue
            
            icon = self.getFullIconUrl( self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?\.jpe?g[^'^"]*?)['"]''')[0] )
            title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<a class="title', '</a>')[1] )
            if title == '': title = self.cleanHtmlStr( self.cm.ph.getSearchGroups(item, '''bubble=['"]([^"^']+?)['"]''')[0] )
            if title == '': title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<h2', '</h2>')[1] )
            
            # get desc
            desc = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<p', '</p>')[1] )
            if desc == '':
                desc = []
                tmp = self.cm.ph.getAllItemsBeetwenMarkers(item, '<td', '</td>')
                if len(tmp): del tmp[0]
                for t in tmp:
                    if '/flags/' in t: t = self.cm.ph.getSearchGroups(t, '''<img[^>]+?src=['"][^"^']+?/([^/]+?)\.png['"]''')[0]
                    t = self.cleanHtmlStr(t)
                    if t != '': desc.append(t)
                desc = ' | '.join(desc)
            
            params = MergeDicts(cItem, {'good_for_fav': True, 'category':nextCategory, 'title':title, 'url':url, 'desc':desc, 'icon':icon})
            self.addDir(params)
            
    def listUjItems(self, cItem):
        try:
            tabID = cItem.get('cat_tab_id', '')
            if tabID == 'mooviecc_ajanlott':
                self.Fzkttm(cItem, tabID)
            elif tabID == 'mooviecc_keresett_tartalom':
                self.Vdakstmk({'name':'history', 'category': 'search', 'cat_tab_id':''}, 'desc', _("Type: "), tabID)
            else:
                return
        except Exception:
            printExc()
            
    def Fzkttm(self, cItem, tabID):
        try:
            self.susn('2', '4', tabID)
            tab_ams = 'mooviecc_ajnlt_musor'
            desc_ams = self.getdvdsz(tab_ams, 'Ajánlott, nézett tartalmak megjelenítése műsorok szerint...')
            tab_adt = 'mooviecc_ajnlt_datum'
            desc_adt = self.getdvdsz(tab_adt, 'Ajánlott, nézett tartalmak megjelenítése dátum szerint...')
            tab_anzt = 'mooviecc_ajnlt_nezettseg'
            desc_anzt = self.getdvdsz(tab_anzt, 'Ajánlott, nézett tartalmak megjelenítése nézettség szerint...')
            A_CAT_TAB = [{'category':'list_third', 'title': 'Dátum szerint', 'cat_tab_id':tab_adt, 'desc':desc_adt},
                         {'category':'list_third', 'title': 'Nézettség szerint', 'cat_tab_id':tab_anzt, 'desc':desc_anzt},
                         {'category':'list_third', 'title': 'Műsorok szerint', 'cat_tab_id':tab_ams, 'desc':desc_ams} 
                        ]
            self.listsTab(A_CAT_TAB, cItem)
        except Exception:
            printExc()
            
    def listThirdItems(self, cItem):
        try:
            tabID = cItem.get('cat_tab_id', '')
            if tabID == 'mooviecc_ajnlt_musor':
                self.Vajnltmsr(cItem)
            elif tabID == 'mooviecc_ajnlt_datum':
                self.Vajnltdtm(cItem)
            elif tabID == 'mooviecc_ajnlt_nezettseg':
                self.Vajnltnztsg(cItem)
            else:
                return
        except Exception:
            printExc()
            
    def Vajnltmsr(self,cItem):
        try:
            self.susn('2', '4', 'mooviecc_ajnlt_musor')
            vtb = self.malvadnav(cItem, '3', '4', '0')
            if len(vtb) > 0:
                for item in vtb:
                    self.addVideo(item)
        except Exception:
            printExc()
            
    def Vajnltdtm(self,cItem):
        vtb = []
        try:
            self.susn('2', '4', 'mooviecc_ajnlt_datum')
            vtb = self.malvadnav(cItem, '4', '4', '0')
            if len(vtb) > 0:
                for item in vtb:
                    self.addVideo(item)
        except Exception:
            printExc()
            
    def Vajnltnztsg(self,cItem):
        try:
            self.susn('2', '4', 'mooviecc_ajnlt_nezettseg')
            vtb = self.malvadnav(cItem, '5', '4', '0')
            if len(vtb) > 0:
                for item in vtb:
                    self.addVideo(item)
        except Exception:
            printExc()
        
    def listItems(self, cItem, nextCategory):
        url = cItem['url']
        sort = cItem.get('f_sort', '')
        
        cItem = dict(cItem)
        if cItem.get('f_query', '') == '':
            sts, data = self.getPage(cItem['url'])
            if not sts: return
            cItem['f_page'] = 1
            tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div id="content">', '<script')[1]
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<input', '>')
            inputCache = {}
            cItem['filters'] = []
            for item in tmp:
                name  = self.cm.ph.getSearchGroups(item, '''name=['"]([^"^']+?)['"]''')[0]
                if name == '': continue
                value = self.cm.ph.getSearchGroups(item, '''value=['"]([^"^']+?)['"]''')[0]
                inputCache[name] = value
            tmp = self.cm.ph.getDataBeetwenMarkers(data, 'function dataFromInput', '}')[1]
            tmp = re.compile('''\[name=([^\]]+?)\]''').findall(tmp)
            for item in tmp:
                cItem['filters'].append(item)
                if item in ['sort', 'page']: continue
                cItem['f_'+item] = inputCache.get(item,  '')
            tmp = self.cm.ph.getDataBeetwenMarkers(data, '$.ajax(', '});', False)[1]
            cItem['url'] = self.getFullUrl(self.cm.ph.getSearchGroups(tmp, '''['"]?url['"]?\s*:\s*['"]([^'^"]+?)['"]''')[0])
            cItem['f_query'] = self.cm.ph.getSearchGroups(tmp, '''['"]?data['"]?\s*:\s*['"]([^'^"]+?)['"]''')[0]
        
        # prepare query
        query = []
        for filter in cItem.get('filters', []):
            name = 'f_'+filter
            if name in cItem:
                value = cItem[name]
                if not str(value).startswith(filter+':'):
                    value = '%s:%s' % (filter, cItem[name])
                if not value.endswith('|'): value += '|'
                query.append(value)
        
        query = cItem.get('f_query', '') + (''.join(query))
        
        urlParams = dict(self.defaultParams)
        urlParams.update({'raw_post_data':True})
        sts, data = self.getPage(cItem['url'], urlParams, query)
        if not sts: return
        
        nextPage = self.cm.ph.getSearchGroups(data, '''pages_num\s*=\s*([0-9]+?)[^0-9]''')[0]
        if nextPage != '' and int(nextPage) > 0:
            nextPage = True
        else: nextPage = False
        
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'id="movie', '<div class="clear')
        for item in data:
            url = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''')[0] )
            if not self.cm.isValidUrl(url): continue
            
            icon = self.getFullIconUrl( self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''')[0] )
            title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<a class="title', '</a>')[1] )
            if title == '': title = self.cleanHtmlStr( self.cm.ph.getSearchGroups(item, '''bubble=['"]([^"^']+?)['"]''')[0] )
            if title == '': title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<h2', '</h2>')[1] )
            desc = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<p', '</p>')[1] )
            
            params = MergeDicts(cItem, {'good_for_fav': True, 'category':nextCategory, 'title':title, 'url':url, 'desc':desc, 'icon':icon})
            self.addDir(params)
        
        if nextPage and len(self.currList) > 0:
            params = dict(cItem)
            params.update({'title':_("Next page"), 'f_page':cItem.get('f_page', 1)+1, 'desc':'Nyugi...\nVan még további tartalom, lapozz tovább!!!'})
            self.addDir(params)
            
    def _listCategories(self, cItem, nextCategory, m1, m2):
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        
        data = self.cm.ph.getDataBeetwenMarkers(data, m1, m2)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div', '</div>')
        for item in data:
            url   = self.getFullUrl(self.cm.ph.getSearchGroups(item, '''href\s*=\s*['"]([^'^"]+?)['"]''')[0])
            title = self.cleanHtmlStr(item)
            params = dict(cItem)
            params.update({'category':nextCategory, 'title':title, 'url':url})
            self.addDir(params)
        
    def listMovies(self, cItem, nextCategory):
        self._listCategories(cItem, nextCategory, 'id="get_movies"', '</li>')
        
    def listSeries(self, cItem, nextCategory):
        self._listCategories(cItem, nextCategory, 'id="get_series"', '</li>')
        
    def listSort(self, cItem, nextCategory):
        if 0 == len(self.cacheSortOrder):
            sts, data = self.getPage(self.getFullUrl('/online-filmek/')) # sort order is same for movies and series
            if not sts: return
            data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="sort_by">', '</ul>')[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
            for item in data:
                if not self.cm.ph.getSearchGroups(item, '''href=['"]([^'^"]+?)['"]''')[0].startswith('javascript'): continue
                sort  = self.cm.ph.getSearchGroups(item, '''id=['"]([^'^"]+?)['"]''')[0]
                if sort == '': continue
                title = self.cleanHtmlStr(item)
                self.cacheSortOrder.append({'title':title, 'f_sort':sort})
        
        for item in self.cacheSortOrder:
            params = dict(cItem)
            params.update({'category':nextCategory})
            params.update(item)
            self.addDir(params)
    
    def _fillLinksCache(self, data, marker):
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, marker, '</table>')
        episodesTab = []
        for tmp in data:
            episodeName = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(tmp, '<h2', '</h2>')[1])
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<tr', '</tr>')
            for item in tmp:
                url = self.cm.ph.getSearchGroups(item, '''href=['"](https?://[^'^"]+?)['"]''')[0]
                tmpUrl = self.cm.ph.getSearchGroups(url, '''/(https?://[^'^"]+?)$''')[0]
                if self.cm.isValidUrl(tmpUrl): url = tmpUrl
                if not self.cm.isValidUrl(url): continue
                serverName = []
                item = self.cm.ph.getAllItemsBeetwenMarkers(item, '<td', '</td>')
                for t in item:
                    if '/flags/' in t:
                        t = self.cm.ph.getSearchGroups(t, '''<img[^>]+?src=['"][^"^']+?/([^/]+?)\.png['"]''')[0]
                    t = self.cleanHtmlStr(t)
                    if t != '': serverName.append(t)
                serverName = ' | '.join(serverName)
                if episodeName not in episodesTab:
                    episodesTab.append(episodeName)
                    self.cacheLinks[episodeName] = []
                self.cacheLinks[episodeName].append({'name':serverName, 'url':url, 'need_resolve':1})
        return episodesTab
    
    def exploreItem(self, cItem, nextCategory=''):
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        if len(data) == 0: return
        desc = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(data, '<div id="plot">', '</div>')[1])
        desc = re.sub(r'^(.{1000}).*$', '\g<1>...', desc)
        icon  = self.cm.ph.getDataBeetwenMarkers(data, '<div id="poster"', '</div>')[1]
        icon  = self.getFullIconUrl( self.cm.ph.getSearchGroups(icon, '''<img[^>]+?src=['"]([^"^']+?\.jpe?g[^"^']*?)["']''')[0] )
        if icon == '': icon = cItem.get('icon', '')
        # trailer 
        #tmp = self.cm.ph.getDataBeetwenMarkers(data, '<a id="youtube_video"', '</a>')[1]
        #url = self.getFullUrl(self.cm.ph.getSearchGroups(tmp, '''href=['"]([^'^"]+?)['"]''')[0])
        #if 1 == self.up.checkHostSupport(url):
        #    title = self.cleanHtmlStr(tmp)
        #    title = '%s - %s' %(cItem['title'], title)
        #    params = dict(cItem)
        #    params.update({'good_for_fav': True, 'title':title, 'prev_title':cItem['title'], 'url':url, 'prev_url':cItem['url'], 'prev_desc':cItem.get('desc', ''), 'icon':icon, 'desc':desc})
        #    self.addVideo(params)
        sourcesLink = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'streambtn'), ('</div', '>'), caseSensitive=False)[1]
        sourcesLink = self.cm.ph.getSearchGroups(sourcesLink, '''href=['"](https?://[^'^"]+?)['"]''')[0]
        if not self.cm.isValidUrl(sourcesLink):
            return
        tmp = urllib.unquote(sourcesLink)
        tmp = self.cm.ph.getSearchGroups(tmp[1:], '''(https?://.+)''')[0]
        if tmp != '': sourcesLink = tmp
        sts, data = self.getPage(sourcesLink)
        if not sts: return []
        if len(data) == 0: return []
        desc2 = self.cm.ph.getDataBeetwenMarkers(data, '<article', '</article>')[1]
        mainTitle = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(desc2, '<h1>', '</h1>')[1])
        if mainTitle == '': mainTitle = cItem['title']
        self.cacheLinks  = {}
        if 'seasonList' in data:
            data = self.cm.ph.getDataBeetwenMarkers(data, '<nav>', '</nav>')[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
            for item in data:
                url = self.cm.ph.getSearchGroups(item, '''href=['"]([^'^"]+?)['"]''')[0]
                if url != '' and not self.cm.isValidUrl(url): 
                    url = urlparse.urljoin(sourcesLink, url)
                title = self.cleanHtmlStr(item)
                params = dict(cItem)
                params.update({'good_for_fav': True, 'category':nextCategory, 'title':title, 'prev_title':mainTitle, 'url':url, 'prev_url':cItem['url'], 'prev_desc':cItem.get('desc', ''), 'icon':icon, 'desc':desc})
                self.addDir(params)
        else:
            desc2 = self.cleanHtmlStr(desc2)
            if desc2 != '': desc = desc2
            desc = re.sub(r'^(.{1000}).*$', '\g<1>...', desc)
            episodesList = self._fillLinksCache(data, '<table')
            for item in episodesList:
                params = dict(cItem)
                params.update({'good_for_fav': True, 'links_key':item, 'title':mainTitle, 'icon':icon, 'desc':desc})
                self.addVideo(params)
            
    def listEpisodes(self, cItem):
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        if len(data) == 0: return
        desc = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(data, '<article', '</article>')[1])
        desc = re.sub(r'^(.{1000}).*$', '\g<1>...', desc)
        seriesTitle = cItem.get('prev_title', '')
        sNum = self.cm.ph.getSearchGroups(cItem['title'], '''^([0-9]+?)\.''')[0]
        episodesList = self._fillLinksCache(data, '<div class="item">')
        for item in episodesList:
            eNum = self.cm.ph.getSearchGroups(item, '''^([0-9]+?)\.''')[0]
            params = dict(cItem)
            title = seriesTitle 
            if eNum != '' and sNum != '': 
                title = '%s - s%se%s' % (seriesTitle, sNum.zfill(2), eNum.zfill(2))
            else:
                title = '%s - %s, %s' % (seriesTitle, cItem['title'], item)
            params.update({'good_for_fav': True, 'title':title, 'links_key':item, 'prev_desc':cItem.get('desc', ''), 'desc':desc})
            self.addVideo(params)

    def listSearchResult(self, cItem, searchPattern, searchType):
        try:
            self.suskrbt('2', '4', searchPattern)
            cItem = dict(cItem)
            cItem['url'] = self.getFullUrl('/core/ajax/movies.php')
            cItem['f_query'] = 'type=search&query=keywords:%s|' % searchPattern
            cItem['f_page'] = 1
            cItem['filters'] = ['page']
            self.listItems(cItem, 'explore_item')
        except Exception:
            return
            
    def mstr(self, i_t=''):
        bv = ''
        try:
            if i_t != '':
                idx1 = i_t.rfind('-')
                if -1 < idx1:
                    tmp_i_t = i_t[idx1+1:].strip()
                    idx2 = tmp_i_t.rfind('e')
                    if -1 < idx2:
                        tmp_i_t = tmp_i_t[idx2+1:].strip()
                        idx3 = len(tmp_i_t)
                        if idx3 == 0 or idx3 > 2: return ''
                        if tmp_i_t.startswith('0'): tmp_i_t = tmp_i_t[1:].strip()
                        bv = tmp_i_t
            return bv
        except Exception:
            return ''
            
    def flzchim(self, i_u='', i_t=''):
        try:
            if i_u != '' and i_t != '':
                self.cacheLinks  = {}
                if 'filmbazis' in i_u:
                    episodesTab = []
                    resz = self.mstr(i_t)
                    if resz != '':
                        sts, data = self.getPage(i_u)
                        if not sts: return
                        if len(data) == 0: return
                        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item">', '</table>')
                        if len(data) == 0: return
                        for tmp in data:
                            id_v = self.cm.ph.getSearchGroups(tmp, '''id=['"]([^'^"]+?)['"]''')[0]
                            if len(id_v) == 0 or id_v != resz: continue
                            episodeName = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(tmp, '<h2', '</h2>')[1])
                            tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<tr', '</tr>')
                            for item in tmp:
                                url = self.cm.ph.getSearchGroups(item, '''href=['"](https?://[^'^"]+?)['"]''')[0]
                                tmpUrl = self.cm.ph.getSearchGroups(url, '''/(https?://[^'^"]+?)$''')[0]
                                if self.cm.isValidUrl(tmpUrl): url = tmpUrl
                                if not self.cm.isValidUrl(url): continue
                                serverName = []
                                item = self.cm.ph.getAllItemsBeetwenMarkers(item, '<td', '</td>')
                                for t in item:
                                    if '/flags/' in t:
                                        t = self.cm.ph.getSearchGroups(t, '''<img[^>]+?src=['"][^"^']+?/([^/]+?)\.png['"]''')[0]
                                    t = self.cleanHtmlStr(t)
                                    if t != '': serverName.append(t)
                                serverName = ' | '.join(serverName)
                                if episodeName not in episodesTab:
                                    episodesTab.append(episodeName)
                                    self.cacheLinks[episodeName] = []
                                self.cacheLinks[episodeName].append({'name':serverName, 'url':url, 'need_resolve':1})
                            break
                if 'moovie' in i_u:
                    sts, data = self.getPage(i_u)
                    if not sts: return
                    if len(data) == 0: return
                    sourcesLink = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'streambtn'), ('</div', '>'), caseSensitive=False)[1]
                    sourcesLink = self.cm.ph.getSearchGroups(sourcesLink, '''href=['"](https?://[^'^"]+?)['"]''')[0]
                    if not self.cm.isValidUrl(sourcesLink): return
                    tmp = urllib.unquote(sourcesLink)
                    tmp = self.cm.ph.getSearchGroups(tmp[1:], '''(https?://.+)''')[0]
                    if tmp != '': sourcesLink = tmp
                    sts, data = self.getPage(sourcesLink)
                    if not sts: return
                    if len(data) == 0: return
                    if 'seasonList' not in data:
                        episodesList = self._fillLinksCache(data, '<table')
        except Exception:
            return
        
    def getLinksForVideo(self, cItem):
        retTab = []
        try:
            if 1 == self.up.checkHostSupport(cItem.get('url', '')):
                videoUrl = cItem['url'].replace('youtu.be/', 'youtube.com/watch?v=')
                return self.up.getVideoLinkExt(videoUrl)
            if cItem['category'] != 'list_third':
                self.susmrgts('2', '4', cItem['tps'], cItem['url'], cItem['title'], cItem['icon'], cItem['desc'])
                key = cItem.get('links_key', '')
            else:
                key = ''
                resz = self.mstr(cItem['title'])
                if resz != '':
                    key = resz + '. rész'
                self.flzchim(cItem['url'], cItem['title'])
            return self.cacheLinks.get(key, [])
        except Exception:
            return []
        
    def getVideoLinks(self, videoUrl):
        videoUrl = strwithmeta(videoUrl)
        urlTab = []
        
        # mark requested link as used one
        if len(self.cacheLinks.keys()):
            for key in self.cacheLinks:
                for idx in range(len(self.cacheLinks[key])):
                    if videoUrl in self.cacheLinks[key][idx]['url']:
                        if not self.cacheLinks[key][idx]['name'].startswith('*'):
                            self.cacheLinks[key][idx]['name'] = '*' + self.cacheLinks[key][idx]['name']
                        break
        
        orginUrl = str(videoUrl)
        url = videoUrl
        post_data = None
        while True:
            sts, data = self.getPage(url, post_data=post_data)
            if not sts: return []
            videoUrl = self.cm.meta['url']
            
            if self.up.getDomain(self.getMainUrl()) in videoUrl or self.up.getDomain(videoUrl) == self.up.getDomain(orginUrl):
                
                if 'captcha' in data: data = re.sub("<!--[\s\S]*?-->", "", data)
                
                if 'google.com/recaptcha/' in data and 'sitekey' in data:
                    message = _('Link protected with google recaptcha v2.')
                    SetIPTVPlayerLastHostError(message)
                    break
                elif '<input name="captcha"' in data:
                    tmp = self.cm.ph.getDataBeetwenMarkers(data, '<content', '</form>')[1]
                    captchaTitle = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(tmp, '<h1', '</h1>')[1])
                    captchaDesc  = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(tmp, '<p', '</p>')[1])
                    
                    # parse form data
                    data = self.cm.ph.getDataBeetwenMarkers(data, '<form', '</form>')[1]
                    
                    imgUrl = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
                    if imgUrl != '' and not imgUrl.startswith('/'): imgUrl = '/' + imgUrl
                    if imgUrl.startswith('/'): imgUrl = urlparse.urljoin(videoUrl, imgUrl)
                    
                    printDBG("img URL [%s]" % imgUrl)
                        
                    actionUrl = self.cm.ph.getSearchGroups(data, 'action="([^"]+?)"')[0]
                    if actionUrl != '': actionUrl = '/' + actionUrl
                    if actionUrl.startswith('/'): actionUrl = urlparse.urljoin(videoUrl, actionUrl)
                    elif actionUrl == '': actionUrl = videoUrl
                        
                    captcha_post_data = dict(re.findall(r'''<input[^>]+?name=["']([^"^']*)["'][^>]+?value=["']([^"^']*)["'][^>]*>''', data))
                    
                    if self.cm.isValidUrl(imgUrl):
                        params = dict(self.defaultParams)
                        params['header'] = dict(params['header'] )
                        params['header']['Accept'] = 'image/png,image/*;q=0.8,*/*;q=0.5'
                        params = dict(self.defaultParams)
                        params.update( {'maintype': 'image', 'subtypes':['jpeg', 'png'], 'check_first_bytes':['\xFF\xD8','\xFF\xD9','\x89\x50\x4E\x47'], 'header':params['header']} )
                        filePath = GetTmpDir('.iptvplayer_captcha.jpg')
                        ret = self.cm.saveWebFile(filePath, imgUrl.replace('&amp;', '&'), params)
                        if not ret.get('sts'):
                            SetIPTVPlayerLastHostError(_('Fail to get "%s".') % imgUrl)
                            return urlTab

                        params = deepcopy(IPTVMultipleInputBox.DEF_PARAMS)
                        params['accep_label'] = _('Send')
                        params['title'] = captchaTitle
                        params['status_text'] = captchaDesc
                        params['with_accept_button'] = True
                        params['list'] = []
                        item = deepcopy(IPTVMultipleInputBox.DEF_INPUT_PARAMS)
                        item['label_size'] = (160,75)
                        item['input_size'] = (480,25)
                        item['icon_path'] = filePath
                        item['title'] = _('Answer')
                        item['input']['text'] = ''
                        params['list'].append(item)
            
                        ret = 0
                        retArg = self.sessionEx.waitForFinishOpen(IPTVMultipleInputBox, params)
                        printDBG(retArg)
                        if retArg and len(retArg) and retArg[0]:
                            printDBG(retArg[0])
                            captcha_post_data['captcha'] = retArg[0][0]
                            post_data = captcha_post_data
                            url = actionUrl
                        
                        if not sts:
                            return urlTab
                        else:
                            continue
                
                found = False
                printDBG(data)
                tmp = re.compile('''<iframe[^>]+?src=['"]([^"^']+?)['"]''', re.IGNORECASE).findall(data)
                for url in tmp:
                    if 1 == self.up.checkHostSupport(url):
                        videoUrl = url
                        found = True
                        break
                if not found or 'flashx' in videoUrl:
                    tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, 'embedFrame', '</a>')
                    tmp.extend(self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>'))
                    for urlItem in tmp:
                        url = self.cm.ph.getSearchGroups(urlItem, '''href=['"](https?://[^'^"]+?)['"]''')[0]
                        if 1 == self.up.checkHostSupport(url):
                            videoUrl = url
                            found = True
                            break
            break
        
        if self.cm.isValidUrl(videoUrl):
            urlTab = self.up.getVideoLinkExt(videoUrl)
        
        return urlTab
    
    def getFavouriteData(self, cItem):
        return json.dumps(cItem) 
        
    def getLinksForFavourite(self, fav_data):
        if self.MAIN_URL == None:
            self.selectDomain()
        links = []
        try:
            cItem = byteify(json.loads(fav_data))
            links = self.getLinksForVideo(cItem)
        except Exception: printExc()
        return links
        
    def setInitListFromFavouriteItem(self, fav_data):
        if self.MAIN_URL == None:
            self.selectDomain()
        try:
            params = byteify(json.loads(fav_data))
        except Exception: 
            params = {}
            printExc()
        self.addDir(params)
        return True
        
    def getArticleContent(self, cItem):
        retTab = []
        otherInfo = {}
        
        url = cItem.get('prev_url', '')
        if url == '': url = cItem.get('url', '')
        
        sts, data = self.getPage(url)
        if not sts: return retTab
        
        title = self.cleanHtmlStr(self.cm.ph.getSearchGroups(data, '''<meta[^>]+?itemprop="name"[^>]+?content="([^"]+?)"''')[0])
        icon  = self.cm.ph.getDataBeetwenMarkers(data, '<div id="poster"', '</div>')[1]
        icon  = self.getFullIconUrl( self.cm.ph.getSearchGroups(icon, '''<img[^>]+?src=['"]([^"^']+?\.jpe?g[^"^']*?)["']''')[0] )
        desc  = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(data, '<div id="plot"', '</div>')[1])
        
        rating = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(data, '<span class="rating_all"', '</div>')[1])
        
        data = self.cm.ph.getDataBeetwenMarkers(data, '<table style="margin-left', '</table>')[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<tr', '</tr>')
        mapDesc = {'Eredeti Cím:': 'alternate_title', 'Év:':'year', 'Játékidő:':'duration', 'IMDb értékelés:':'imdb_rating',
                   'Kategória:':'category', 'Írta:':'writers', 'Rendezte:':'directors', 'Szereplők:':'actors'} #'Megtekintve:':'views',
        for item in data:
            item = self.cm.ph.getAllItemsBeetwenMarkers(item, '<td', '</td>')
            if len(item) != 2: continue
            marker = self.cleanHtmlStr(item[0])
            tmp  =  self.cm.ph.getAllItemsBeetwenMarkers(item[1], '<a', '</a>')
            value = []
            for t in tmp:
                t = self.cleanHtmlStr(t)
                if t != '': value.append(t)
            if len(value): value = ', '.join(value)
            else: value = self.cleanHtmlStr(item[1])
            if value == '': continue
            key = mapDesc.get(marker, '')
            if key != '': otherInfo[key] = value
            
        if rating != '': otherInfo['rating'] = rating
        
        if title == '': title = cItem['title']
        if desc == '':  desc = cItem.get('desc', '')
        if icon == '':  icon = cItem.get('icon', self.DEFAULT_ICON_URL)
        
        return [{'title':self.cleanHtmlStr( title ), 'text': self.cleanHtmlStr( desc ), 'images':[{'title':'', 'url':self.getFullUrl(icon)}], 'other_info':otherInfo}]
    
    def suskrbt(self, i_md='', i_hgk='', i_mpsz=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzwbywERxYklKkl5BRgEAD/4T/Q=='))
        try:
            if i_mpsz != '' and len(i_mpsz) > 1:
                if len(i_mpsz) > 80:
                    i_mpsz = i_mpsz[:78]
                i_mpsz = base64.b64encode(i_mpsz).replace('\n', '').strip()
                if i_hgk != '':
                    i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
                    pstd = {'md':i_md, 'hgk':i_hgk, 'mpsz':i_mpsz}
                    if i_md != '' and i_hgk != '' and i_mpsz != '':
                        sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
            return
        except Exception:
            return
            
    def susmrgts(self, i_md='', i_hgk='', i_mptip='', i_mpu='', i_mpt='', i_mpi='', i_mpdl=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzy0tSQQTxYklKUl6BRkFABGoFBk='))
        try:
            if i_hgk != '': i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
            if i_mptip != '': i_mptip = base64.b64encode(i_mptip).replace('\n', '').strip()
            if i_mpu != '': i_mpu = base64.b64encode(i_mpu).replace('\n', '').strip()
            if i_mpt != '': i_mpt = base64.b64encode(i_mpt).replace('\n', '').strip()
            if i_mpi == '':
                i_mpi = base64.b64encode('-')
            else:
                i_mpi = base64.b64encode(i_mpi).replace('\n', '').strip()
            if i_mpdl == '':
                i_mpdl = base64.b64encode('-')
            else:
                i_mpdl = base64.b64encode(i_mpdl).replace('\n', '').strip()
            pstd = {'md':i_md, 'hgk':i_hgk, 'mptip':i_mptip, 'mpu':i_mpu, 'mpt':i_mpt, 'mpi':i_mpi, 'mpdl':i_mpdl}
            if i_md != '' and i_hgk != '' and i_mptip != '' and i_mpu != '':
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
            return
        except Exception:
            return
    
    def getdvdsz(self, pu='', psz=''):
        bv = ''
        if pu != '' and psz != '':
            n_atnav = self.malvadst('1', '4', pu)
            if n_atnav != '' and self.aid:
                if pu == 'mooviecc_filmek':
                    self.aid_ki = 'ID: ' + n_atnav + '  |  Mooviecc  v' + HOST_VERSION + '\n'
                else:
                    self.aid_ki = 'ID: ' + n_atnav + '\n'
            else:
                if pu == 'mooviecc_filmek':
                    self.aid_ki = 'Mooviecc  v' + HOST_VERSION + '\n'
                else:
                    self.aid_ki = ''
            bv = self.aid_ki + psz
        return bv
        
    def malvadst(self, i_md='', i_hgk='', i_mpu=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUL04sSdQvS8wD0ilJegUZBQD8FROZ'))
        pstd = {'md':i_md, 'hgk':i_hgk, 'mpu':i_mpu}
        t_s = ''
        temp_vn = ''
        temp_vni = ''
        try:
            if i_md != '' and i_hgk != '' and i_mpu != '':
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
                if not sts: return t_s
                if len(data) == 0: return t_s
                data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="div_a_div', '</div>')[1]
                if len(data) == 0: return t_s
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<input', '/>')
                if len(data) == 0: return t_s
                for item in data:
                    t_i = self.cm.ph.getSearchGroups(item, 'id=[\'"]([^"^\']+?)[\'"]')[0]
                    if t_i == 'vn':
                        temp_vn = self.cm.ph.getSearchGroups(item, 'value=[\'"]([^"^\']+?)[\'"]')[0]
                    elif t_i == 'vni':
                        temp_vni = self.cm.ph.getSearchGroups(item, 'value=[\'"]([^"^\']+?)[\'"]')[0]
                if temp_vn != '':
                    t_s = temp_vn
            return t_s
        except Exception:
            return t_s
            
    def malvadnav(self, cItem, i_md='', i_hgk='', i_mptip=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzy0tSQQTxYklKUl6BRkFABGoFBk='))
        t_s = []
        try:
            if i_md != '' and i_hgk != '' and i_mptip != '':
                if i_hgk != '': i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
                if i_mptip != '': i_mptip = base64.b64encode(i_mptip).replace('\n', '').strip()
                pstd = {'md':i_md, 'hgk':i_hgk, 'mptip':i_mptip}
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
                if not sts: return t_s
                if len(data) == 0: return t_s
                data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="div_a1_div"', '<div id="div_a2_div"')[1]
                if len(data) == 0: return t_s
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="d_sor_d"', '</div>')
                if len(data) == 0: return t_s
                for temp_item in data:
                    temp_data = self.cm.ph.getAllItemsBeetwenMarkers(temp_item, '<span', '</span>')
                    if len(temp_data) == 0: return t_s
                    for item in temp_data:
                        t_vp = self.cm.ph.getSearchGroups(item, 'class=[\'"]([^"^\']+?)[\'"]')[0]
                        if t_vp == 'c_sor_u':
                            temp_u = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_u">', '</span>', False)[1]
                            if temp_u != '': temp_u = base64.b64decode(temp_u)
                        if t_vp == 'c_sor_t':
                            temp_t = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_t">', '</span>', False)[1]
                            if temp_t != '': temp_t = base64.b64decode(temp_t)
                        if t_vp == 'c_sor_i':
                            temp_i = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_i">', '</span>', False)[1]
                            if temp_i != '': temp_i = base64.b64decode(temp_i)
                        if t_vp == 'c_sor_l':
                            temp_l = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_l">', '</span>', False)[1]
                            if temp_l != '': temp_l = base64.b64decode(temp_l)
                        if t_vp == 'c_sor_n':
                            temp_n = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_n">', '</span>', False)[1]
                            if temp_n != '': temp_n = base64.b64decode(temp_n)
                        if t_vp == 'c_sor_tip':
                            temp_tp = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_tip">', '</span>', False)[1]
                            if temp_tp != '': temp_tp = base64.b64decode(temp_tp)
                    if temp_u == '' and temp_t =='': continue
                    if temp_n == '': temp_n = '1'
                    params = MergeDicts(cItem, {'good_for_fav': True, 'url':temp_u, 'title':temp_t, 'icon':temp_i, 'desc':temp_l, 'nztsg':temp_n, 'tps':temp_tp})
                    t_s.append(params)       
            return t_s
        except Exception:
            return []
            
    def susn(self, i_md='', i_hgk='', i_mpu=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUL04sSdQvS8wD0ilJegUZBQD8FROZ'))
        pstd = {'md':i_md, 'hgk':i_hgk, 'mpu':i_mpu, 'hv':self.vivn, 'orv':self.porv, 'bts':self.pbtp}
        try:
            if i_md != '' and i_hgk != '' and i_mpu != '':
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
            return
        except Exception:
            return
    
    def ebbtit(self):
        try:
            if '' == self.btps.strip() or '' == self.brdr.strip():
                msg = 'A Set-top-Box típusát és a használt rendszer (image) nevét egyszer meg kell adni!\n\nA kompatibilitás és a megfelelő használat miatt kellenek ezek az adatok a programnak.\nKérlek, a helyes működéshez a valóságnak megfelelően írd be azokat.\n\nA "HU Telepítő" keretrendszerben tudod ezt megtenni.\n\nKilépek és megyek azt beállítani?'
                ret = self.sessionEx.waitForFinishOpen(MessageBox, msg, type=MessageBox.TYPE_YESNO, default=True)
                return False
            else:
                return True
        except Exception:
            return False
    
    def gits(self):
        bv = '-'
        tt = []
        try:
            if fileExists(zlib.decompress(base64.b64decode('eJzTTy1J1s8sLi5NBQATXQPE'))):
                fr = open(zlib.decompress(base64.b64decode('eJzTTy1J1s8sLi5NBQATXQPE')),'r')
                for ln in fr:
                    ln = ln.rstrip('\n')
                    if ln != '':
                        tt.append(ln)
                fr.close()
                if len(tt) == 1:
                    bv = tt[0].strip()[:-6].capitalize()
                if len(tt) == 2:
                    bv = tt[1].strip()[:-6].capitalize()
            return bv
        except:
            return '-'
            
    def malvadkrttmk(self, i_md='', i_hgk=''):
        bv = []
        ukszrz = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzwbywERxYklKkl5BRgEAD/4T/Q=='))
        try:
            if i_md != '' and i_hgk != '':
                i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
                pstd = {'md':i_md, 'hgk':i_hgk}
                sts, data = self.cm.getPage(ukszrz, self.defaultParams, pstd)
                if not sts: return []
                if len(data) == 0: return []
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div>', '</div>', False)
                if len(data) == 0: return []
                for item in data:
                    if item != '':
                        bv.append(base64.b64decode(item))
            return bv
        except Exception:
            return []
            
    def Vdakstmk(self, baseItem={'name': 'history', 'category': 'search'}, desc_key='plot', desc_base=(_("Type: ")), tabID='' ):
        if tabID != '':
            self.susn('2', '4', tabID)
            
        def _vdakstmk(data,lnp=50):
            ln = 0
            for histItem in data:
                plot = ''
                try:
                    ln += 1
                    if type(histItem) == type({}):
                        pattern = histItem.get('pattern', '')
                        search_type = histItem.get('type', '')
                        if '' != search_type: plot = desc_base + _(search_type)
                    else:
                        pattern = histItem
                        search_type = None
                    params = dict(baseItem)
                    params.update({'title': pattern, 'search_type': search_type,  desc_key: plot, 'tps':'0'})
                    self.addDir(params)
                    if ln >= lnp:
                        break
                except Exception: printExc()
            
        try:
            list = self.malvadkrttmk('1','4')
            if len(list) > 0:
                _vdakstmk(list,2)
            if len(list) > 0:
                list = list[2:]
                random.shuffle(list)
                _vdakstmk(list,48)
        except Exception:
            printExc()
    
    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        mode     = self.currItem.get("mode", '')
        self.currList = []
        if name == None:
            self.listMainMenu( {'name':'category'} )
        elif category == 'list_movies':
            if self.currItem['cat_tab_id'] == 'mooviecc_filmek':
                self.susn('2', '4', 'mooviecc_filmek')
            self.listsTab(self.MOVIES_CAT_TAB, self.currItem)
        elif category == 'list_series':
            if self.currItem['cat_tab_id'] == 'mooviecc_sorozatok':
                self.susn('2', '4', 'mooviecc_sorozatok')
            self.listsTab(self.SERIES_CAT_TAB, self.currItem)
        elif category == 'movies_cats':
            self.listMovies(self.currItem, 'list_sort')
        elif category == 'series_cats':
            self.listSeries(self.currItem, 'list_sort')
        elif category == 'list_sort':
            self.listSort(self.currItem, 'list_items')
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'list_main':
            if self.currItem['cat_tab_id'] == 'mooviecc_legjobbak':
                self.susn('2', '4', 'mooviecc_legjobbak')
            if self.currItem['cat_tab_id'] == 'mooviecc_most_nezik':
                self.susn('2', '4', 'mooviecc_most_nezik')
            self.listMainItems(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem, 'list_episodes')
        elif category == 'list_episodes':
            self.listEpisodes(self.currItem)
        elif category == 'list_uj':
            self.listUjItems(self.currItem)
        elif category == 'list_third':
            self.listThirdItems(self.currItem)
        elif category in ["search", "search_next_page"]:
            if self.currItem['cat_tab_id'] == 'mooviecc_kereses':
                self.susn('2', '4', 'mooviecc_kereses')
            cItem = dict(self.currItem)
            cItem.update({'search_item':False, 'name':'category'}) 
            self.listSearchResult(cItem, searchPattern, searchType)
        elif category == "search_history":
            if self.currItem['cat_tab_id'] == 'mooviecc_kereses_elozmeny':
                self.susn('2', '4', 'mooviecc_kereses_elozmeny')
            self.listsHistory({'name':'history', 'category': 'search', 'cat_tab_id':'', 'tps':'0'}, 'desc', _("Type: "))
        else:
            printExc()
        CBaseHostClass.endHandleService(self, index, refresh)

class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, MoovieCC(), True, [])
        
    def withArticleContent(self, cItem):
        if (cItem['type'] != 'video' and cItem['category'] != 'explore_item'):
            return False
        return True
    
    