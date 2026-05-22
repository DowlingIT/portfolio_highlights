# Elab Session Handling

## Introduction

Intro video: [Intro Video](https://lablynx.scicloud.net/apps/files/?dir=/Share/INTERNAL%20LLX%20TRAINING&openfile=1670981)

Abstraction of the default IIS / ASP session handling is implemented in order to:

- Enable web farm highly available failover for web servers
- Enable user login sessions to persist and not be affected by web server application pool restarts/recycles
- Enable Elab.Net elements to be built in such a way that we can gradually transition the asp web pages to newer technologies

ASP web sessions are in memory, with no option to configure for storage in cookies, or SQL. As a result, user information in web sessions is not present on a secondary server in a web farm, or in a newly started web session. Further, ASP.NET sites and asp sites handle session data differently, even if both technologies are served by IIS under a common web site domain (ie llx.lablynx.com).

Features, loosely termed “Session Abstraction,” are implemented that enable web session data storage in SQL Server to be saved, and loaded, as needed across web sessions and technologies. This was initially built to permit an Elab 7.16.4 client to recycle application pools more frequently, due to frequent corruption of session data. COTS release is planned to occur with Elab 7.21. The design maintained as small a footprint as possible on existing COTS code to minimize difficulties upgrading for that client. There are elements of these features that COTS code in Elab 7.20 will reset, and so the simplest time to implement will be during an upgrade to version 7.21.

## Design Considerations

Design of Session Abstraction is also respective of the fact that we plan to upgrade away from ASP to newer technologies. Newer technologies, such as ASP.Net have this functionality built in to their frameworks, and so this will not require LabLynx coded upgrades. Most of the code is in files that are separate from the main code base, and will never require upgrade. Storage has been built into tables that [ASP.Net](http://ASP.Net) also utilizes, though the session data is serialized differently.

At the time of writing (8/15/23), Elab.Net has no need to participate in the exchange of abstracted user session data. It will, but that will likely wait until the metadata foundation is present such that it can present pages based on the Elab metadata framework. The code is present for Elab Classic to permit exchange. Elab.Net will need to know which data to grab, and how to load and save, when the time comes.

A method of exchanging a single ASP web session with [ASP.Net](http://ASP.Net) is also present, as of Elab 7.20. While this method has been available for quite a long time, it was difficult to make work, and had issues running under SSL secured sites. Changes were implemented with Elab 7.20 to simplify, in order for features built with that release to function as intended.

## Terminology

The standalone word “session” will be avoided in this document, as it would be ambiguous between session cookies, the web sessions managed by IIS / ASP and the newly coined term “Elab User Session”.

As the document progresses, additional terminology will be introduced. A definition without proper context is more likely to cause confusion.

- **IIS:** The application on a server that is configured to host web sites on that server, thus making the server a “web server.”
- **Web session:** The sessions that are managed by IIS on behalf of hosted web sites. IIS handles web sessions differently for ASP and [ASP.Net](http://ASP.Net), and where context requires, these will be specified. Each web session has a unique identifier, called a **Session ID**.

  There is normally just one session per browser that accesses the site - which corresponds to one user per web session, when users are logged in.

  Technologies that handle web sessions differently will, with respect to the browser, each have web sessions of their own. For example, asp and [asp.net](http://asp.net). So, use of a web site that has both of these technologies by one user/browser will have a single web session under asp, and another under [asp.net](http://asp.net).

  Web sessions end either when a user has been inactive for a defined period of time (by default 20 minutes), or when the browser is closed.

- **Application:** When a web site is accessed for the first time, the web server will start an “Application Pool” that has a “Worker Process.” Events occur when this is started, and when it is terminated are accessible from code. There is an in-memory key pair variable store that is kept with the worker process. These “application variables” are accessible to all server side code served by that web server, for the web site(s) that are served by that application pool, and will have the same values regardless of web session, and thus, for all users.
- **Cookie:** A unit of storage that is maintained by the browser, and usually set by the Web server. Relevant to this article, cookies are sent between the browser and the web server identified by the domain known to the cookie (ie. [llx.lablynx.com](http://llx.lablynx.com)). As a result, if there are multiple technological elements that otherwise do not share data - such as two web servers in a web farm, or Elab (asp) and [ELab.Net](http://ELab.Net) ([asp.net](http://asp.net)) - the cookie data provides a means of data exchange.

  Cookies are identified by a code-provided name.

- **Session Cookie:** A cookie that has no expiry set will be deleted when the Web Session ends.
- **Persisted Cookie:** A cookie that has a set expiry, and which the browser will delete at the indicated UTC time.
- **Web Farm:** More than one web server will serve the web site. Since the publicly accessible URL must resolve (via DNS) to a single place, and decisions must be made about which server to use, there is generally a load balancer device in front of the web servers. There are a variety of ways to configure for high availability, failover, and other scenarios. An example is shown below based on AWS. The actual web sites are served by the EC2 instances in this example. They do not directly share data stored in memory, such as web session or application variables.

![Web Farm Example](Elab+Session+Handling_files/image001.png)

## Session Abstraction Scenarios

### Principles

A cookie stored on a users web browser can persist data beyond any actions taken on any individual technology or web server. As can database data, however, this sits on the other side of the web server from a web browser, and so is not capable of tracking browser activity, or in turn, user activity.

Cookies track data by domain (eg llx.lablynx.com). Thus, when a web site is configured to serve from multiple technologies or web servers that are not capable of simple, direct exchange of information on their own, cookies can store data that can let servers know where to look for that information.

As cookies are visible to savvy users, sensitive data should not be stored within.

Thus, to handle the various scenarios that are anticipated, we have:

1. Browser cookies that will track where to find information about a user.
2. Web servers and technologies that use cookie data to find information, or be made aware of actions or information taken by other web servers or technologies.
3. Session data that is synced to the database, such that this can be synced to locations other than the one that saved the data. Thus, native session handling is used, but the database data is used to sync data in those web sessions as users log in, log out, visit pages, and so on.

### Terminology

These are features coded to manage scenarios involved in managing data according to the principles noted above.

- **Provider:** The software that coordinates all data exchanges and initialization for activity that occurs within an application pool.
- **Session Manager:** Used by an instance of the provider, the software that manages the status of the browser cookie, and synchronization status of web session to database session data. The Provider, based on events that it is made aware of, in turn will alert the Session Manager to make appropriate updates.

  There is one server side instance of the “state” of the class per user web session (stored in the web session variables). This state allows instances of the session manager class to be created with the correct information, as needed, by the provider.

- **Repository:** Used by an instance of the provider, the software used to save and retrieve web session data to the database, as needed by the web server. Utilized by the provider, instances of repositories are created and disposed of as needed.

  The database stores a single entry for all shared session data that is json serialized, as directed by the session manager.

- **Elab Cookie:** Made up term for the cookie managed by the Session Manager. This helps avoid confusing terminology with “session cookie,” which is defined above per industry (for example: [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)).
- **Login cookies:** There are session cookies used to help with timezone and to ensure that access to reports and files is made under a valid login. These are normally set at login, but, being session cookies, are lost when the browser is closed.
- **SQL ID:** Unique identifier kept with cookie that is used to ID relevant data stored in the database.
- **App ID:** Identifiers that are unique to the applications. In a web farm, configuration will be needed. Different technologies may simply use constants that the web farm configs would extend.

## Scenario Table

The table below runs through scenarios in increasingly complicated order, such that simpler scenarios can be inferred (and thus not revisited). This table does a few things. One - there are a lot of moving parts; this provides a reference point for intended functionality. Two - it provides a reference for situations that should be tested when making changes. Three - it provides context when troubleshooting. Four - helped initial developer “rubber-duck” through logic.

Bolded entries under “Event” indicate starts of different scenarios. A couple of initial one liners are mentioned that apply to all further scenarios.

Videos (covering the table scenarios below):

- Testing: [Video of various test scenarios](https://lablynx.scicloud.net/apps/files/?dir=/Share/INTERNAL%20LLX%20TRAINING&openfile=1671095)
  - including login/out/session expiry
  - activity of elab cookie, sql data and login/out data is shown
  - Restarts of web server and browser during user sessions
  - Chrome & Firefox
  - Multiple users

This is not expected to run threaded or asynchronously under Elab. There may be race conditions which cannot be readily addressed, and which are not considered, below. The most likely area they might occur would be between tech (Elab and Elab.Net used during same page request/submit).

| Scenario | Event | Web Cookie | Server/Tech | Database |
|----------|-------|------------|-------------|----------|
| Elab standalone | User logged in, visits any page | Load: Check sync state - good | | End: save session data, add watermark indicating which server/app last saved and when. |
| | Web session Idle Timeout reached | Elab Cookie deleted by browser | | Session entries purged |
| | Open App (session recycle while logged in & 2 users) | Init new Elab Cookie as session cookie. SQL ID set based on Session ID. | Init singleton Session Manager in session vars for user 1 | Init session data entry |
| | User 1 login | Elab cookie persisted based on UI configured session timeout | | Page visit events in login process will save session data |
| | User 2 load + login (rest of user 2 actions same as #1) | Init new Elab Cookie as session cookie (user 2). SQL ID set based on Session ID for user 2. | Init singleton Session Manager in session vars for user 2 | Init session data entry |
| | Session Recycle | Check sync state - find user logged in via cookie, but not via web session vars, and different Session ID. Update sessionid in Elab cookie. Rebuild login cookies | App and session vars lost. Init singleton Session Manager in session vars. Load session data | Web session data loaded from SQL ID |
| | User 1 logout | Elab cookie set to expire so that it is deleted by browser. On next visit - Init new Elab Cookie as session cookie. SQL ID set based on Session ID. | | Page visit events in logout process will save session data |
| | User 1 Browser close | Elab cookie disposed | | |
| | Open App (browser closed / reopened while logged in) | Init new Elab Cookie as session cookie. SQL ID set based on Session ID. | Init singleton Session Manager in session vars | Init session data entry |
| | User login | Elab cookie persisted based on UI configured session timeout | | Page visit events in login process will save session data |
| | User browser close | Session cookies lost (but not Elab cookie) | Web session vars lost | |
| | User opens app again, prior to expiry | Check sync state - find user logged in via cookie, but not via web session vars, and different Session ID. Update sessionid in Elab cookie. Rebuild login cookies | Init singleton Session Manager in session vars | Web session data loaded from SQL ID |
| | Open App (browser closed / reopened after timeout) | Init new Elab Cookie as session cookie. SQL ID set based on Session ID. | Init singleton Session Manager in session vars | Init session data entry |
| | User login | Elab cookie persisted based on UI configured session timeout | | Page visit events in login process will save session data |
| | User browser close | Session cookies lost. Elab cookie lost | Web session vars lost | |
| | User opens app again, after expiry | Init new Elab Cookie as session cookie. SQL ID set based on Session ID. | Init singleton Session Manager in session vars | Init session data entry |

## Elab Session for Cross Session Data Exchange

The core principles for this are discussed in some detail under the “Session Abstraction Scenarios” section, above. Design details are presented below, for a deeper dive into where to find code, and what it does.

### Config

Config will only be required if setting Elab web servers up in a web farm. In that case, each server requires a unique identifier. This will be addended to the constant that identifies the app, in the provider code.

In `LimsInfo.xml` in the “AppInfo” section, setup a key value pair for “webFarmId.” For example:

![Config Example](Elab+Session+Handling_files/image002.png)

Each server in the web farm must have this, and the value on each web server must be unique.

### Design

Design heavily based on open source, MIT licensed ASP.Net session management: [https://github.com/aspnet/AspNetSessionState](https://github.com/aspnet/AspNetSessionState)

Where things differ: Method of serializing session data, and provider/manager/store logic. ASP.Net directly uses this for session management, where the Elab solution is syncing native sessions against the web session data saved to the database.

Any uses of this feature should create only an instance of the Provider (`SqlSessionStateProvider`). The provider handles the rest. Make sure to dispose when done (set xx=Nothing) and appropriately handle any errors.

![Design Diagram](Elab+Session+Handling_files/image004.png)

#### Class Purposes

- **SqlSessionStateProvider:** See “Provider” under Scenarios, above.
- **SqlSessionStore:** An error handling Scripting.Dictionary, used as needed, to load session data to be serialized and stored in the database
- **ElabSessionManager:** See “Session Manager” under Scenarios, above
- **SqlSessionStateRepository:** See “Repository” under Scenarios, above
    - Note that this also has code to create the schema used by this solution, checked and executed as the provider starts up.
- **SessionItem:** The single json serialized session data for storage in the database
- **SqlSessionStateRepositoryUtil:** Utility class to assist the repository with database querying
- **SqlCommandHelper:** Utility for building ADODB.Command objects to be used with ADODB.Connections for execution and querying of the database.
- **DataRS:** A recordset that handles database errors and cleans up after itself on disposals.
- **SqlExceptionCheck:** A central class to handle database errors that cleans up after itself on disposals
- **Sec:** Seconds for various time periods, up to a year
- **SqlParameterCollectionExtension:** Used in conjunction with SqlCommandHelper. Most ADO command objects for stored procs are building the requisite command parameters in code, rather than letting ADO build the parameters via a “refresh” action. This helps avoid more trips to the DB than needed, and maximize performance. This class assists in readability and centralization for adding these parameters to commands.
- **SqlParameterName:** Collection of variables to use, rather than strings, when identifying the parameters on stored procs
- **SesErrorItem:** Stores information about any particular error that is caught by error catching code
- **SqlSessionErrorStack:** A stack of SesErrorItems. The “ToString()” method will provide a string of all errors that were observed. When used correctly, each class/method in the stack will be included in the message.

The overall solution is expected to take action at only a few critical events:

![Critical Events](Elab+Session+Handling_files/image006.png)

#### Class Reference Notes

Reference material to ease development and troubleshooting. Class structure for the highest level classes. Utilities, helpers, error trapping, etc are intentionally left out.

| Class | Object | Desc | Type | Output |
|-------|--------|------|------|--------|
| SqlSessionStateProvider | Construct (connectionstring) |  | Public Default Function | Class instance |
|  | App_Start() | See “App Start,” above | Public Sub |  |
|  | StartSession() | See “Sess Start,” above | Public Sub |  |
|  | UserLogin() | See “Login,” above | Public Sub |  |
|  | UserLogout() | See “Logout,” above | Public Sub |  |
|  | ResponseStart() | See “Response Start,” above | Public Sub |  |
|  | ResponseEnd() | See “Response End,” above | Public Sub |  |
|  | SyncSession (SyncActions, SessionMgr) |  | Private Sub |  |
|  | SessionDataToSql(SessionMgr) |  | Private Sub |  |
|  | SQLDataToSessionStore (SessionManager) |  | Private Sub |  |
|  | GetTimeout (SessionManager) |  | Private Function | If cookie has timeout, user timeout, else 20m |
|  | PurgeIfNeeded() |  | Private Sub |  |
|  | GetDBId (SessionManager) |  | Private Function | Primary key of data in DB to use |
|  | PurgeSessions () |  | Private Sub |  |
|  | Deserialize_JSON (obj) |  | Private Function | Json object |
|  | IsNullOrWhitespace (obj) |  | Private Function | T/F |
|  | BytesToString (bytes) |  | Private Function | String from UTF8 bytes |
|  | StringToBytes (str) |  | Private Function | UTF8 bytes of string |
| SqlSessionStore | Items |  | Public Get Property | Dictionary of items in store |
|  | AddOrUpdateItem(Key, Value) |  | Public Sub |  |
|  | RemoveItem (Key) |  | Public Sub |  |
|  | toJSON() |  | Public Function | Json serialized store items |
| ElabSessionManager | Construct(ErrStack, state) |  | Public Default Function | Class instance |
|  | BuildFromStateString(state) |  | Private Sub |  |
|  | CurrentState |  | Public Get Property |  |

#### Class Error Handling Notes

Uses of the session handling code are meant to handle any errors that occur, via the appropriate use of an instance of the provider. All errors can be handled via the standard Err object, including any database or JSON serialization errors. The provider instance will log errors to the database (event log).

The below notes may be used in conjunction with the design diagram to understand any handled error “bubbling.”

- **SqlParameterName** - no special error handling, just var assignment
- **Sec** - no special error handling, just var assignment
- **SQLExceptionCheck** - construct wraps, passes Err.number. Otherwise, no special error handling. DB errors are not thrown. Does check for DB errors via a function call, which passes the error message back.
- **DataRS** - DB errors are caught - if present, Message and HasDBError functions should be checked by caller. No special Err handling.
- **SqlSessionStateRepositoryUtil** - construct wraps, passes Err.number. Otherwise, normal for Err. DB errors are caught and raised as Err.Number 60000
- **SqlParameterCollectionExtension** - no special err handling
- **SqlCommandHelper** - construct wraps, passes Err.number. Otherwise normal. CreateSProcIfDoesNotExist ignores database errors.
- **SessionItem** - Construct wraps, passes Err.number. Otherwise normal, no special handling.
- **SqlSessionStateRepository** - Construct & public functions/subs wrap & re-raise Err.number. DB errors are caught and raised as Err.Number 60000 (including uses of SqlCommandHelper .CreateSProcIfDoesNotExist). The function LogErrorToDB ignores DB errors, to avoid potential for infinite error loops.
- **ElabSessionManager** - no special error handling, except when getting user timeout value from DB, where error is wrapped and reraised.
- **SqlSessionStateProvider** - Construct wrap & re-raise Err.number. Public functions/subs do the same, but also log error to DB.

## Cookie and Session State Data

Labels intentionally obfuscated for cookies, for added layer of security. Abbreviated for cookie state for brevity. A reference table helped save time in initial dev, and should help save time in future work.

<!-- The HTML has a table here, but the content is not present in the HTML, so nothing to restore. -->

## Other Misc Notes

- **Session.SessionID should not be used for most purposes.** At the time of login, and when sessions are restored from databases, Session("SessionId") is set. Like the SQL Database ID, this value is expected to contain the initial SessionID, not necessarily the current.

    - What this impacts:
        - Login/logout checks, such as happens in sysalert.asp
        - EDD processing, where sessionID is used to stage data
        - Certain Excel and report Elab.Net features.
        - Object tracking features
        - Audit trail entries
        - Possibly, the associated file features that create zips or that can merge multiple PDFs

    - Because the sync features of cookie/DB to and from session are getting the session("sessionid") value, all servers should, after login, behave as if they’re part of this session, even though their Session.SessionID value will be different.

    - This was largely built with the SessionID being used as a variable rather than Session.SessionID through most of application in the first place, and we were able to simply take advantage. Still, this will be important to know in future daily work.

- The call at the end of the response needs to occur before the response is flushed, for those pages that use response.flush

## Providing Session Data for Specified Variables to Elab.Net from Elab Classic

The principle for this is that Elab.Net requires a single variable from Elab classic, and directly requests it.

This feature has existed, but was updated with Elab version 7.20. No changes made during later work for session abstraction. With the work on abstraction above, these will be directly available in the .net sessions. However, not all clients are on 7.21+ just yet, and we will need to maintain backward compatibility until such a time.

In [Elab.Net](http://Elab.Net) (repository elabstudio), the class “ASPSessionVar” is defined in the below file. This class will make ajax calls from server side code to the ASP classic application, asking for particular session variable values. This was originally intended to stay entirely server side, however https/ssl setup precludes this capability. Thus, this logic will/should only work when a user is logged in, and has valid session UserID and ProfileID variables set in Elab Classic.

![ASPSessionVar Example](Elab+Session+Handling_files/image008.png)

When an elab.net page needs to request a specific variable, it can create an instance of this class, and then ask for data with the “GetsSessionVar” class method. For example:

![GetsSessionVar Example](Elab+Session+Handling_files/image010.png)

### Config

- **Web.Config → Configuration → AppSettings → ASPSessionVarSite**
    - Looks for the file ”SessionVar.asp” in the relative directory specified.
    - Default value should be an empty string, which will find the COTS “SessionVar.asp” in the root of the elab application folder.
    - A custom ”SessionVar.asp” file could be placed in the cs_scripts folder, and this configuration value adjusted to use it, rather than the COTS one. Make sure to secure any such files against random use.