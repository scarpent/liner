#!/bin/bash

coverage run -m unittest liner_test
coverage report -m --omit=/usr/*
