"""
Run feelpp model for one config
"""
from typing import List

import os
from math import fabs 

import json

import re
import pandas as pd
from tabulate import tabulate

from .params import getparam
from .solver import init, solve
# from ..units import load_units


def oneconfig(feelpp_directory, jsonmodel, args, targets: dict, parameters: dict):
    """
    Run a simulation until currents are reached
    
    targets: dict of target (name: objectif , csv, ...)
    parameters: all jsonmodel parameters
    """

    table_values = []
    table_headers = []
    
    pwd = os.getcwd()
    print(f"oneconfig: workingdir={pwd}")
    basedir = os.path.dirname(args.cfgfile)
    print(f'jsonmodel={jsonmodel}')
    print(f'basedir={basedir}')
    
    # init feelpp env
    (feelpp_env, feel_pb) = init(args, feelpp_directory)
    if feelpp_env.isMasterRank():
        print(f"oneconfig: after feelpp init workingdir={os.getcwd()}")

    """
    # init U field
    Xh = fpp.functionSpace(space="Pch", mesh=feel_pb.mesh(), order=1)
    usave = Xh.element()

    for target, values in targets.items():
        params = []
        for p in values['control_params']:
            tmp = getparam(p[0], parameters, p[1], args.debug)
            params += tmp

        for param in params:
            marker = param.replace('U_','')
            # print(f'marker: {marker}, goal={values["goals"][marker].iloc[-1]} xx')
            value = float(parameters[param])
            usave.on(range=fpp.markedelements(feel_pb.mesh(), marker), expr=fpp.expr(str(value)))

    usave.save(os.getcwd(), name='U_new')
    """

    for target, values in targets.items():
        if args.debug and feelpp_env.isMasterRank():
            print(f"{target}: {values['objectif']}")
        table_values.append(float(values['objectif']))
        table_headers.append(f'{target}[{values["unit"]}]')    # print("targets:", targets)

    # capture actual params per target:
    # {target: {"pname0": value, "pname1": value, ...}}
    params = {}
    for key, values in targets.items():
        params[key] = []
        for p in values['control_params']:
            if args.debug:
                print(f"extract control params for {p[0]}")
            tmp = getparam(p[0], parameters, p[1], args.debug)
            params[key] += tmp

    # print(f'targets: {targets}')
    print(f'params: {params}')

    (bcparams, _Current_df) = solve(feelpp_env, feel_pb, f'{pwd}/{jsonmodel}', args, targets, params, parameters)

    if feelpp_env.isMasterRank():
        print(f"oneconfig: after solve workingdir={ os.getcwd() }")
    exit(1)

    # update
    results = {}
    update(cwd, jsonmodel, params, control_params, bc_params, value, args.debug)
    """
    for objectif in objectifs:
        dict_df = {}
        
        (name, value, params, control_params, bc_params, targets, pfields, postvalues, pvalues) = objectif
        update(cwd, jsonmodel, params, control_params, bc_params, value, args.debug)
        if args.debug and feelpp_env.isMasterRank():
            print(f'bcparams[{name}]: {bcparams[name]}')
        # print(f'params: {params}')

        df = getTarget(pvalues['Power'], feelpp_env, args.debug)
        table_headers.append('R[Ohm]')
        table_values.append(float(df.iloc[-1][0]/(value*value)))
        if not df.empty and feelpp_env.isMasterRank():
            print(f"I: {value} [A]\tPower: {df.iloc[-1][0]} [W]")
   
        filename = os.path.join(os.getcwd(), 'magnetic.measures/values.csv')
        if os.path.isfile(filename):
            for field in ['Inductance', 'B0']:
                df = getTarget(field, feelpp_env, args.debug)
                table_headers.append(f'{field}[getTargetUnit{field}]')
                table_values.append(float(df.iloc[-1][0]))
                if feelpp_env.isMasterRank():
                    print(f'magnetic: {field}={df.iloc[-1][0]}')
        else:
            if feelpp_env.isMasterRank():
                print(f'{filename}: no such file')

        if feelpp_env.isMasterRank():
            print(f'Save tables to csv files: workingdir={os.getcwd()}')

        # Stats - to be displayed in results
        for p in pfields:
            df = getTarget(p, feelpp_env, args.debug)
            if not df.empty:
                # create new key dict
                keys = df.columns.values.tolist()
                nkeys = {}
                for item in keys:
                    nitem = item
                    if re.match(targetdefs[p]['rematch'], item):
                        regexp = re.split('_', targetdefs[p]['rematch'])
                        nitem = item.replace(regexp[0], '')
                        nitem = nitem.replace(regexp[1], '')
                        nitem = nitem.replace(regexp[3], '')
                        nitem = nitem.replace('__', '')
                        # remove _ if nitem end
                        if nitem.endswith('_'):
                            nitem = nitem[:-1]
                        # print(f"{p}: {nitem}")
                    nkeys[item] = nitem

                # remove all rows except latest row
                df.rename(columns=nkeys, inplace=True)
                if feelpp_env.isMasterRank():
                    print(f"{p} [{targetdefs[p]['unit']}]:\n{tabulate(df, headers='keys', tablefmt='simple')}\n")

                _df = df.drop(range(len(df.index)-1))
                # print(f'_df={_df.transpose()}')
                dict_df[p] = _df

        if args.debug and feelpp_env.isMasterRank():
            print(f'dict_df: {dict_df.keys()}')
            print("params:", params)
            print("bc_params:", bc_params)

        # Compute R per part
        _df = dict_df[pvalues['PowerH']]
        (nrows, ncolumns) = _df.shape
        for i in range(ncolumns):
            _value = float(_df.iloc[-1,i])/(value*value)
            table_headers.append(f"R{i}[Ohm]")
            table_values.append(_value)

        # save cooling params to csv
        for p in pfields:
            if p in dict_df:
                _df = dict_df[p]
                unit = f'{p}[{getTargetUnit(p)}]'
                _df.rename(index={1: unit}, inplace=True)

        _values = {}

        for param in bcparams[name]:
            table_headers.append(f"{param}[{bcparams[name][param]['unit']}]")
            _value = bcparams[name][param]['value']
            table_values.append(_value)
            if re.match('^h\\d+', param):
                _name = f"Channel{param.replace('h','')}"
            if re.match('^dTw\\d+', param):
                _name = f"Channel{param.replace('dTw','')}"
            _values[_name] = [_value]
            
        _h_df = pd.DataFrame(_values, index=['h[W/m2/K]','Tw[K]','dTw[K]'])
        _Cooling_df = pd.concat([_h_df, dict_df[pvalues['Flux']]])
        if args.debug and feelpp_env.isMasterRank():
            print(f'_Cooling_df: {_Cooling_df}')
        os.makedirs('cooling.measures', exist_ok=True)
        _Cooling_df.to_csv('cooling.measures/postvalues.csv', index=True)

        # Temp stats
                    
        _T_df = pd.concat([dict_df[p] for p in postvalues['T']], sort=True)
        for p in postvalues['T']:
            _T_df.rename(index={f"{p}[{getTargetUnit(p)}]": f"{p.replace('H','')}[{getTargetUnit(p)}]"}, inplace=True)
        if args.debug and feelpp_env.isMasterRank():
            print(f'_T_df = {_T_df}')
        _T_df.to_csv('heat.measures/postvalues.csv', index=True)

        # Stress, VonMises stats
        if postvalues['Stress'][0] in dict_df:
            _Stress_df = pd.concat([dict_df[p] for p in postValues['Stress']], sort=True)
            for p in postvalues["Stress"]:
                _Stress_df.rename(index={f"{p}[{unit}]": f"{p}[{unit}]"}, inplace=True)
            if feelpp_env.isMasterRank():
                print(f'_Stress_df = {_Stress_df}')
            _Stress_df.to_csv('elastic.measures/postvalues.csv', index=True)

        if feelpp_env.isMasterRank():
            print(f"Commissionning:\n{tabulate([table_values], headers=table_headers, tablefmt='simple')}\n")
    
        results[name] = (table_headers, table_values)
        """
    
    return results
