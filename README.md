# Finance Manager
Managing HEI forecasting and budget setting data. 

This python command-line app is desinged to be used by system admin to maintain and run a forecasting and budget setting system. End-users use a Power App to actually interface. 

## Data ##

### Model ###

For versatility and to allow for more complete documentation, the app uses [SQLAlchemy's Object Relational Mapper](https://docs.sqlalchemy.org/en/13/orm/index.html) to specify the data model used by the app and the interface. The [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) package is used to migrate changes to the actual database. 

### Key objects ### 

The **Set** object is unique by cost centre, type (budget, forecast etc.), and academic year. For example, There would be 1 *budget* set for cost centre *x* in academic year *y*. Changes to set's input information (via the interface) overrides the previous versions: in this sense, that set is analogous to a file. Note however that the actual finances are intentionally disconnected from this process: finances are instead created as snapshots of sets at a given point in time.



## Interface Access ##

Users can be given permissions to access **cost centres**. Access to a cost centre allows the user to see all finances and details of that cost centre's **sets**. 

