"""
General i18n utility functions.
"""
import cherrypy
import babel.core
import logging


__all__ = ['get_locale']

def lang_in_gettext_format(lang):
    if len(lang) > 2:
        country = lang[3:].upper()
        lang = lang[:2] + "_" + country
    return lang


def parse_http_accept_header(accept):
    """Parse an HTTP Accept header (RFC 2616) into a sorted list.

    The quality factors in the header determine the sort order.
    The values can include possible media-range parameters.
    This function can also be used for the Accept-Charset,
    Accept-Encoding and Accept-Language headers.

    """
    if not accept:
        return []
    items = []
    for item in accept.split(','):
        params = item.split(';')
        for i, param in enumerate(params[1:]):
            param = param.split('=', 1)
            if param[0].strip() == 'q':
                try:
                    q = float(param[1])
                    if not 0 < q <= 1:
                        raise ValueError
                except (IndexError, ValueError):
                    q = 0
                else:
                    item = ';'.join(params[:i+1])
                break
        else:
            q = 1
        if q:
            item = item.strip()
            if item:
                items.append((item, q))
    items.sort(lambda i1, i2: cmp(i2[1], i1[1]))
    return [item[0] for item in items]

def get_accept_languages(accept):
    """Returns a list of languages, by order of preference, based on an
    HTTP Accept-Language string.See W3C RFC 2616
    (http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html) for specification.
    """
    return map(lang_in_gettext_format,
               parse_http_accept_header(accept))

def get_locale(locale=None):

    if locale:
        return locale

    try:
        return babel.core.Locale.parse(cherrypy.session['locale'])
    except AttributeError:
        cherrypy.log.error(
            'Error when trying to get locale, likely due to session tools '
            'not being enabled yet\n',
            '[startup]', severity=logging.ERROR, traceback=True)
    except (ImportError, KeyError):
        pass # we're at the login page and apparently it cannot get rpc
    except babel.core.UnknownLocaleError:
        pass

    try:
        accept_language = cherrypy.request.headers.get("Accept-Language")
        for candidate_language in get_accept_languages(accept_language):
            try:
                return babel.core.Locale.parse(candidate_language)
            except babel.core.UnknownLocaleError:
                cherrypy.log.error("Unknown locale '%s' from Accept-Language "
                                   "header '%s', skipping to next locale",
                                   context="i18n", severity=logging.WARN)
                # Locale Babel does not know about, go to next
                pass
    except AttributeError:
        pass

    return babel.core.Locale("en")
