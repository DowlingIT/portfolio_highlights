Teaching an Old Application to Remember: Session State for ASP Classic

A laboratory SaaS application running on an older Microsoft web stack had a problem with its short-term memory. Web sessions lived in the web server's RAM, which meant every worker process recycle threw eighty to a hundred analysts back to the login screen mid-task. For one long-time client on a decade-old server, it was happening near-weekly. They were ready to shop for a replacement.

The honest part of this story: we never found the root cause. Months of investigation pointed at a worn-out OS we could nudge but not name. So the work changed shape. Instead of fixing the server, we taught the application not to need the server's memory.

The fix did double duty. The application's roadmap called for a piece-by-piece migration to newer .NET technology, which needed old and new code to share user sessions. I borrowed Microsoft's ASP.NET session-state provider pattern (provider, manager, repository), rebuilt it for ASP Classic, and stored the data in the same SQL Server tables ASP.NET itself uses. Application pool recycles became invisible to users, and the migration path lit up.

A useful side benefit: with sessions out of any one server's memory, the application can also run in a true web farm. The client stayed. Years later, they still are.

Stack: ASP Classic, IIS, SQL Server, ASP.NET session-state provider pattern (modeled on AspNetSessionState), strangler fig migration
