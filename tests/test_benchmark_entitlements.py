import numpy as np
import pandas as pd
import pytest

from nsebot.research.benchmark_entitlements import wealth_curve


def fixture():
    dates=pd.date_range('2025-01-01',periods=6)
    parent={'P':pd.Series([100.,100.,80.,40.,40.,40.],index=dates)}
    children={'C':pd.Series([21.,22.],index=dates[4:])}
    events=[dict(parent='P',child='C',type='demerger',ex_date=str(dates[2].date()),numerator=1,denominator=1),
            dict(parent='P',type='bonus',ex_date=str(dates[3].date()),numerator=1,denominator=1)]
    return dates,parent,children,events


def test_receivable_is_neither_cash_nor_a_fabricated_traded_price():
    dates,parent,children,events=fixture()
    original=children['C'].copy()
    frame,result=wealth_curve({'P':{'qty':10}},0.,parent,children,events,dates,{'C':20.},1000.)
    assert frame['marked_equity'].tolist()==[1000.,1000.,1000.,1000.,1010.,1020.]
    assert frame['quoted_equity'].iloc[2:4].isna().all()
    assert frame['indicative_receivable_value'].iloc[2:4].tolist()==[200.,200.]
    assert result['terminal_quantities']=={'P':20,'C':10}
    assert result['indicative_valuation_sessions']==2
    assert result['full_period_observed_benchmark_risk'] is None
    pd.testing.assert_series_equal(original,children['C'])  # No bars were inserted.


def test_missing_child_quote_after_listing_is_rejected_without_filling():
    dates,parent,children,events=fixture()
    children['C']=children['C'].iloc[:1]
    with pytest.raises(ValueError,match='missing listed child price'):
        wealth_curve({'P':{'qty':10}},0.,parent,children,events,dates,{'C':20.},1000.)


def test_missing_parent_quote_is_rejected_without_filling():
    dates,parent,children,events=fixture()
    parent['P']=parent['P'].drop(dates[2])
    with pytest.raises(ValueError,match='missing parent traded close'):
        wealth_curve({'P':{'qty':10}},0.,parent,children,events,dates,{'C':20.},1000.)
