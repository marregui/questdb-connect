import datetime

import questdb_connect as qdbc
import sqlalchemy as sqla
from sqlalchemy.orm import Session

from tests.conftest import (
    ALL_TYPES_TABLE_NAME,
    METRICS_TABLE_NAME,
    collect_select_all,
    collect_select_all_raw_connection,
    wait_until_table_is_ready,
)


def test_insert(test_engine, test_model):
    with test_engine.connect() as conn:
        assert test_engine.dialect.has_table(conn, ALL_TYPES_TABLE_NAME)
        assert not test_engine.dialect.has_table(conn, 'scorchio')
        now = datetime.datetime(2023, 4, 12, 23, 55, 59, 342380)
        now_date = now.date()
        expected = ("(True, 8, 12, 13, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                    "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                    "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                    "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')\n"
                    "(True, 8, 12, 13, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                    "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                    "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                    "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')")
        insert_stmt = sqla.insert(test_model).values(
            col_boolean=True,
            col_byte=8,
            col_short=12,
            col_int=13,
            col_long=14,
            col_float=15.234,
            col_double=16.88993244,
            col_symbol='coconut',
            col_string='banana',
            col_char='C',
            col_uuid='6d5eb038-63d1-4971-8484-30c16e13de5b',
            col_date=now_date,
            col_ts=now,
            col_geohash='dfvgsj2vptwu',
            col_long256='0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
            col_varchar='pineapple'
        )
        conn.execute(insert_stmt)
        conn.execute(sqla.insert(test_model), {
            'col_boolean': True,
            'col_byte': 8,
            'col_short': 12,
            'col_int': 13,
            'col_long': 14,
            'col_float': 15.234,
            'col_double': 16.88993244,
            'col_symbol': 'coconut',
            'col_string': 'banana',
            'col_char': 'C',
            'col_uuid': '6d5eb038-63d1-4971-8484-30c16e13de5b',
            'col_date': now_date,
            'col_ts': now,
            'col_geohash': 'dfvgsj2vptwu',
            'col_long256': '0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
            'col_varchar': 'pineapple'
        })
        assert collect_select_all(conn, expected_rows=2) == expected
    assert collect_select_all_raw_connection(test_engine, expected_rows=2) == expected


def test_inspect_1(test_engine, test_model):
    now = datetime.datetime(2023, 4, 12, 23, 55, 59, 342380)
    now_date = now.date()
    session = Session(test_engine)
    try:
        session.add(test_model(
            col_boolean=True,
            col_byte=8,
            col_short=12,
            col_int=0,
            col_long=14,
            col_float=15.234,
            col_double=16.88993244,
            col_symbol='coconut',
            col_string='banana',
            col_char='C',
            col_uuid='6d5eb038-63d1-4971-8484-30c16e13de5b',
            col_date=now_date,
            col_ts=now,
            col_geohash='dfvgsj2vptwu',
            col_long256='0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
            col_varchar='pineapple'
        ))
        session.commit()
    finally:
        if session:
            session.close()
    metadata = sqla.MetaData()
    table = sqla.Table(ALL_TYPES_TABLE_NAME, metadata, autoload_with=test_engine)
    table_columns = str([(col.name, col.type, col.primary_key) for col in table.columns])
    assert table_columns == str([
        ('col_boolean', qdbc.Boolean(), False),
        ('col_byte', qdbc.Byte(), False),
        ('col_short', qdbc.Short(), False),
        ('col_int', qdbc.Int(), False),
        ('col_long', qdbc.Long(), False),
        ('col_float', qdbc.Float(), False),
        ('col_double', qdbc.Double(), False),
        ('col_symbol', qdbc.Symbol(), False),
        ('col_string', qdbc.String(), False),
        ('col_char', qdbc.Char(), False),
        ('col_uuid', qdbc.UUID(), False),
        ('col_date', qdbc.Date(), False),
        ('col_ts', qdbc.Timestamp(), True),
        ('col_geohash', qdbc.GeohashInt(), False),
        ('col_long256', qdbc.Long256(), False),
        ('col_varchar', qdbc.Varchar(), False),
    ])


def test_inspect_2(test_engine, test_metrics):
    metadata = sqla.MetaData()
    table = sqla.Table(METRICS_TABLE_NAME, metadata, autoload_with=test_engine)
    table_columns = str([(col.name, col.type, col.primary_key) for col in table.columns])
    assert table_columns == str([
        ('source', qdbc.Symbol(), False),
        ('attr_name', qdbc.Symbol(), False),
        ('attr_value', qdbc.Double(), False),
        ('ts', qdbc.Timestamp(), True),
    ])


def test_multiple_insert(test_engine, test_model):
    now = datetime.datetime(2023, 4, 12, 23, 55, 59, 342380)
    now_date = now.date()
    session = Session(test_engine)
    num_rows = 3
    expected = ("(True, 8, 12, 0, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')\n"
                "(True, 8, 12, 1, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')\n"
                "(True, 8, 12, 2, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')")
    try:
        for idx in range(num_rows):
            session.add(test_model(
                col_boolean=True,
                col_byte=8,
                col_short=12,
                col_int=idx,
                col_long=14,
                col_float=15.234,
                col_double=16.88993244,
                col_symbol='coconut',
                col_string='banana',
                col_char='C',
                col_uuid='6d5eb038-63d1-4971-8484-30c16e13de5b',
                col_date=now_date,
                col_ts=now,
                col_geohash='dfvgsj2vptwu',
                col_long256='0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
                col_varchar='pineapple'
            ))
            session.commit()
        assert collect_select_all(session, expected_rows=num_rows) == expected
    finally:
        if session:
            session.close()
        assert collect_select_all_raw_connection(test_engine, expected_rows=num_rows) == expected


def test_bulk_insert(test_engine, test_model):
    now = datetime.datetime(2023, 4, 12, 23, 55, 59, 342380)
    now_date = now.date()
    session = Session(test_engine)
    num_rows = 3
    expected = ("(True, 8, 12, 0, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')\n"
                "(True, 8, 12, 1, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')\n"
                "(True, 8, 12, 2, 14, 15.234, 16.88993244, 'coconut', 'banana', 'C', "
                "UUID('6d5eb038-63d1-4971-8484-30c16e13de5b'), datetime.datetime(2023, 4, 12, "
                "0, 0), datetime.datetime(2023, 4, 12, 23, 55, 59, 342380), 'dfvgsj', "
                "'0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a', 'pineapple')")
    models = [
        test_model(
            col_boolean=True,
            col_byte=8,
            col_short=12,
            col_int=idx,
            col_long=14,
            col_float=15.234,
            col_double=16.88993244,
            col_symbol='coconut',
            col_string='banana',
            col_char='C',
            col_uuid='6d5eb038-63d1-4971-8484-30c16e13de5b',
            col_date=now_date,
            col_ts=now,
            col_geohash='dfvgsj2vptwu',
            col_long256='0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
            col_varchar='pineapple'
        ) for idx in range(num_rows)
    ]
    try:
        session.bulk_save_objects(models)
        session.commit()
        assert collect_select_all(session, expected_rows=num_rows) == expected
    finally:
        if session:
            session.close()
        assert collect_select_all_raw_connection(test_engine, expected_rows=num_rows) == expected


def test_dialect_get_schema_names(test_engine):
    dialect = qdbc.QuestDBDialect()
    with test_engine.connect() as conn:
        assert dialect.get_schema_names(conn) == ["public"]


def test_dialect_get_table_names(test_engine):
    dialect = qdbc.QuestDBDialect()
    with test_engine.connect() as conn:
        table_names = dialect.get_table_names(conn, schema="public")
        assert table_names == dialect.get_table_names(conn)
        assert len(table_names) > 0


def test_dialect_has_table(test_engine):
    dialect = qdbc.QuestDBDialect()
    with test_engine.connect() as conn:
        for table_name in dialect.get_table_names(conn):
            if not dialect.has_table(conn, table_name):
                raise AssertionError()
            if not dialect.has_table(conn, table_name, schema="public"):
                raise AssertionError()


def test_functions(test_engine):
    with test_engine.connect() as conn:
        sql = sqla.text("SELECT name FROM functions()")
        expected = [row[0] for row in conn.execute(sql).fetchall()]
        assert qdbc.get_functions_list() == expected


def test_keywords(test_engine):
    with test_engine.connect() as conn:
        sql = sqla.text("SELECT keyword FROM keywords()")
        expected = [row[0] for row in conn.execute(sql).fetchall()]
        assert qdbc.get_keywords_list() == expected


def test_limit_clause_basic(test_engine, test_model):
    """Test basic LIMIT clause functionality."""
    now = datetime.datetime(2023, 4, 12, 23, 55, 59, 342380)
    now_date = now.date()
    session = Session(test_engine)
    num_rows = 10

    try:
        # Insert test data
        models = [
            test_model(
                col_boolean=True,
                col_byte=8,
                col_short=12,
                col_int=idx,  # Using idx to make rows distinct and ordered
                col_long=14,
                col_float=15.234,
                col_double=16.88993244,
                col_symbol='coconut',
                col_string='banana',
                col_char='C',
                col_uuid='6d5eb038-63d1-4971-8484-30c16e13de5b',
                col_date=now_date,
                col_ts=now,
                col_geohash='dfvgsj2vptwu',
                col_long256='0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
                col_varchar='pineapple'
            ) for idx in range(num_rows)
        ]
        session.bulk_save_objects(models)
        session.commit()

        metadata = sqla.MetaData()
        table = sqla.Table(ALL_TYPES_TABLE_NAME, metadata, autoload_with=test_engine)

        wait_until_table_is_ready(test_engine, ALL_TYPES_TABLE_NAME, num_rows)

        with test_engine.connect() as conn:
            # simple LIMIT
            query = sqla.select(table).limit(5)
            result = conn.execute(query)
            rows = result.fetchall()
            assert len(rows) == 5
            assert rows[0].col_int == 0
            assert rows[-1].col_int == 4

            # LIMIT with OFFSET
            query = sqla.select(table).limit(3).offset(2)
            result = conn.execute(query)
            rows = result.fetchall()
            assert len(rows) == 3
            assert rows[0].col_int == 2
            assert rows[-1].col_int == 4

            # OFFSET only
            query = sqla.select(table).offset(8)
            result = conn.execute(query)
            rows = result.fetchall()
            assert len(rows) == 2
            assert rows[0].col_int == 8
            assert rows[-1].col_int == 9

            # LIMIT 0
            query = sqla.select(table).limit(0)
            result = conn.execute(query)
            rows = result.fetchall()
            assert len(rows) == 0

            # LIMIT 0 and offset
            query = sqla.select(table).limit(0).offset(1)
            result = conn.execute(query)
            rows = result.fetchall()
            assert len(rows) == 0

    finally:
        if session:
            session.close()


def test_limit_clause_with_binds_and_expressions(test_engine, test_model):
    """Test LIMIT clause with bind parameters and expressions."""
    # Setup test data
    now = datetime.datetime(2023, 4, 12, 23, 55, 59, 342380)
    now_date = now.date()
    session = Session(test_engine)
    num_rows = 10

    try:
        # Insert test data
        models = [
            test_model(
                col_boolean=True,
                col_byte=8,
                col_short=12,
                col_int=idx,  # Using idx to make rows distinct and ordered
                col_long=14,
                col_float=15.234,
                col_double=16.88993244,
                col_symbol='coconut',
                col_string='banana',
                col_char='C',
                col_uuid='6d5eb038-63d1-4971-8484-30c16e13de5b',
                col_date=now_date,
                col_ts=now,
                col_geohash='dfvgsj2vptwu',
                col_long256='0xa3b400fcf6ed707d710d5d4e672305203ed3cc6254d1cefe313e4a465861f42a',
                col_varchar='pineapple'
            ) for idx in range(num_rows)
        ]
        session.bulk_save_objects(models)
        session.commit()

        metadata = sqla.MetaData()
        table = sqla.Table(ALL_TYPES_TABLE_NAME, metadata, autoload_with=test_engine)

        wait_until_table_is_ready(test_engine, ALL_TYPES_TABLE_NAME, num_rows)

        with test_engine.connect() as conn:
            # simple bindparam
            result = conn.execute(
                sqla.select(table).limit(sqla.bindparam('limit_val')),
                {"limit_val": 5}
            )
            rows = result.fetchall()
            assert len(rows) == 5
            assert rows[0].col_int == 0
            assert rows[-1].col_int == 4

            # bindparam with expressions
            result = conn.execute(
                sqla.select(table).limit(sqla.bindparam('base_limit') * 2),
                {"base_limit": 3}
            )
            rows = result.fetchall()
            assert len(rows) == 6
            assert rows[0].col_int == 0
            assert rows[-1].col_int == 5

            # multiple bindparams in expression
            result = conn.execute(
                sqla.select(table).limit(
                    sqla.bindparam('limit_val')
                ).offset(
                    sqla.bindparam('offset_val')
                ),
                {
                    "limit_val": 3,
                    "offset_val": 2
                }
            )
            rows = result.fetchall()
            assert len(rows) == 3
            assert rows[0].col_int == 2
            assert rows[-1].col_int == 4

            # bindparam with type specification
            from sqlalchemy import Integer
            result = conn.execute(
                sqla.select(table).limit(
                    sqla.bindparam('limit_val', type_=Integer) + 1
                ),
                {"limit_val": 4}
            )
            rows = result.fetchall()
            assert len(rows) == 5
            assert rows[0].col_int == 0
            assert rows[-1].col_int == 4

            # text() and bindparam
            from sqlalchemy import text
            result = conn.execute(
                text("SELECT * FROM all_types_table LIMIT :lo, :hi"),
                {"lo": 3, "hi": 8}
            )
            rows = result.fetchall()
            assert len(rows) == 5
            assert rows[0].col_int == 3
            assert rows[-1].col_int == 7

    finally:
        if session:
            session.close()
