#!/bin/bash

coverage run -m unittest discover tests
coverage report -m --omit=/usr/*
#coverage html -m --omit=/usr/*

