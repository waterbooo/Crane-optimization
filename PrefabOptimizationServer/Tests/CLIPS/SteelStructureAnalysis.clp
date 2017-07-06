;;;***********************************************************
;;;*              Steel Structure Analysis                   *
;;;*   Takes set of facts for a steel structural model       *
;;;*   Makes analysis of beams, connections and columns      *
;;;***********************************************************

;;=====================================
;;=======General model check rules=====
;;=====================================

(defrule hello
=>
(printout t "Hello World." crlf)
)

(deftemplate project-data
    (slot frame-system-type)
)

(deftemplate model-result
	(slot frame-system-valid)
)

; Checks whether frame system has a not valid type
(defrule wrong-frame-system-type
    (declare (salience 10000))
    (project-data (frame-system-type ?systype))
    (and
		(test (<> (str-compare ?systype SMF) 0))
		(test (<> (str-compare ?systype IMF) 0))
    )
=>
    (assert (model-frame-system-valid FALSE))
    (printout t "Got into the wrong system rule." crlf)
)

; Checks whether frame system has a valid type
(defrule correct-frame-system-type
    (declare (salience 10000))
    (project-data (frame-system-type ?systype))
    (not
	    (and
			(test (<> (str-compare ?systype SMF) 0))
			(test (<> (str-compare ?systype IMF) 0))
	    )
    )
=>
   (assert (model-frame-system-valid TRUE))
   (printout t "Got into the correct system rule." crlf)
)

;Fills model check result
(defrule gather-model-results
	(declare (salience 9999))
	(model-frame-system-valid ?res)
=>
	(assert (model-result (frame-system-valid ?res)))
)

;;=====================================
;;=======Connection checks rules=======
;;=====================================
(deftemplate connection-data
    (slot id)
	(slot type)
	(slot beam-id)
	(slot column-id)
	(slot max-beam-size)
	(slot min-beam-size)
	(slot max-beam-linear-weight)
	(slot max-beam-flange-thickness)
	(slot min-beam-flange-thickness)
	(slot min-clear-span-depth-ratio)
	(slot max-column-depth)
	(slot web-to-thickness-ratio-ok-beam)
	(slot web-to-thickness-ratio-ok-column)
)

(deftemplate connection-result
	(slot id)
	(slot metadata-ok)
)

; Checks whether connection type is not supported
(defrule unsupported-connection-type
    (declare (salience 9999))
    (connection-data (id ?conn-id) (type ?conn-type))
    (or
		(test (= (str-compare ?conn-type None) 0))
		(test (= (str-compare ?conn-type Unknown) 0))
    )
=>
    (assert (connection-type-supported ?conn-id FALSE))
)

; Checks whether connection type is supported
(defrule supported-connection-type
    (declare (salience 9999))
	(connection-data (id ?conn-id) (type ?conn-type))
    (not
	    (or
			(test (= (str-compare ?conn-type None) 0))
			(test (= (str-compare ?conn-type Unknown) 0))
	    )
    )
=>
    (assert (connection-type-supported ?conn-id TRUE))
)

;Checks whether connection metadata is ok
(defrule check-metadata-requirements 
    (declare (salience 9998))
    (connection-data (id ?conn-id))
    (connection-type-supported ?conn-id ?ok)
=>
    (assert (connection-result (id ?conn-id) (metadata-ok ?ok)))
)

;;==============================================================
;;=======Beam in connection check rules from BuildLogic=========
;;==============================================================
(deftemplate beam-data
    (slot id)
	(slot member-production-procedure)
	(slot rolled-shapes)
	(slot size)	
	(slot weight-per-lf)
	(slot top-flange-thickness)
	(slot cut-length)
	(slot depth)
)

(deftemplate beam-result
	(slot id)
	(slot conn-id)
	(slot beam-shape-to-production-procedure-valid)
	(slot size-to-range-valid)
	(slot weight-per-lf-to-max-linear-weight-valid)
	(slot flange-thickness-to-range-valid)
	(slot cutlength-depth-ratio-to-min-clear-ratio-valid)
	(slot web-to-thickness-beam-ratio-valid)
)

;Checks whether beam shape is supported
(defrule valid-beam-shape-to-production-procedure
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-size ?maxbs) (min-beam-size ?minbs))
	(beam-data (id ?beam-id) (member-production-procedure ?mpp) (rolled-shapes ?rs) (size ?size))
	(and
		(test (= (str-compare ?mpp Rolled) 0))
		(test (= (str-compare ?rs WideFlange) 0))
	)
	=>
	(assert (beam-shape-to-production-procedure-valid ?conn-id ?beam-id TRUE))
)

;Checks whether beam shape is not supported
(defrule not-valid-beam-shape-to-production-procedure
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-size ?maxbs) (min-beam-size ?minbs))
	(beam-data (id ?beam-id) (member-production-procedure ?mpp) (rolled-shapes ?rs) (size ?size))
	(not
		(and
			(test (= (str-compare ?mpp Rolled) 0))
			(test (= (str-compare ?rs WideFlange) 0))
		)
	)
	=>
	(assert (beam-shape-to-production-procedure-valid ?conn-id ?beam-id FALSE))
)

;Checks whether beam size is in allowed range for the connection
(defrule valid-size-to-range
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-size ?maxbs) (min-beam-size ?minbs))
	(beam-data (id ?beam-id) (size ?size))
	(and
		(test (<= ?size ?maxbs))
		(test (>= ?size ?minbs))
	)
	=>
	(assert (size-to-range-valid ?conn-id ?beam-id TRUE))
)

;Checks whether beam size is not in allowed range for the connection
(defrule not-valid-size-to-range
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-size ?maxbs) (min-beam-size ?minbs))
	(beam-data (id ?beam-id) (size ?size))
	(not
		(and
			(test (<= ?size ?maxbs))
			(test (>= ?size ?minbs))
		)
	)
	=>
	(assert (size-to-range-valid ?conn-id ?beam-id FALSE))
)

;Checks whether beam's weight per lf is less than maximum allowed weight
(defrule valid-weight-to-max-linear-weight
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-linear-weight ?maxblw))
	(beam-data (id ?beam-id) (weight-per-lf ?vpl))
	(test (<= ?vpl ?maxblw))
	=>
	(assert (weight-per-lf-to-max-linear-weight-valid ?conn-id ?beam-id TRUE))
)

;Checks whether beam's weight per lf is not less than maximum allowed weight
(defrule not-valid-weight-to-max-linear-weight
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-linear-weight ?maxblw))
	(beam-data (id ?beam-id) (weight-per-lf ?vpl))
	(not (test (<= ?vpl ?maxblw)))
	=>
	(assert (weight-per-lf-to-max-linear-weight-valid ?conn-id ?beam-id FALSE))
)

;Checks whether beam flange thickness is in allowed for connection range
(defrule valid-flange-thickness-to-range
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-flange-thickness ?maxbft) (min-beam-flange-thickness ?minbft))
	(beam-data (id ?beam-id) (top-flange-thickness ?tft))
	(and
		(test (<= ?tft ?maxbft))
		(test (>= ?tft ?minbft))
	)
	=>
	(assert (flange-thickness-to-range-valid ?conn-id ?beam-id TRUE))
)

;Checks whether beam flange thickness is not in allowed for connection range
(defrule not-valid-flange-thickness-to-range
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (max-beam-flange-thickness ?maxbft) (min-beam-flange-thickness ?minbft))
	(beam-data (id ?beam-id) (top-flange-thickness ?tft))
	(not
		(and
			(test (<= ?tft ?maxbft))
			(test (>= ?tft ?minbft))
		)
	)
	=>
	(assert (flange-thickness-to-range-valid ?conn-id ?beam-id FALSE))
)

;Checks whether beam cut-length to depth is greater or equal than minimum span to depth ratio for connection
(defrule valid-cutlength-depth-ratio-to-min-clear-ratio
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (min-clear-span-depth-ratio ?mincsdr))
	(beam-data (id ?beam-id) (cut-length ?cl) (depth ?d))
	(test (<= ?mincsdr (/ ?cl ?d)))
	=>
	(assert (cutlength-depth-ratio-to-min-clear-ratio-valid ?conn-id ?beam-id TRUE))
)

;Checks whether beam cut-length to depth is not greater or equal than minimum span to depth ratio for connection
(defrule not-valid-cutlength-depth-ratio-to-min-clear-ratio
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (min-clear-span-depth-ratio ?mincsdr))
	(beam-data (id ?beam-id) (cut-length ?cl) (depth ?d))
	(test (> ?mincsdr (/ ?cl ?d)))
	=>
	(assert (cutlength-depth-ratio-to-min-clear-ratio-valid ?conn-id ?beam-id FALSE))
)

;Checks whether beam web to thickness ratio is ok for current connection
(defrule valid-web-to-thickness-beam-ratio
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (web-to-thickness-ratio-ok-beam ?ok))
	(test (= (str-compare ?ok TRUE) 0))
	=>
	(assert (web-to-thickness-beam-ratio-valid ?conn-id ?beam-id TRUE))
)

;Checks whether beam web to thickness ratio is not ok for current connection
(defrule not-valid-web-to-thickness-beam-ratio
    (declare (salience 9997))
	(connection-data (id ?conn-id) (beam-id ?beam-id) (web-to-thickness-ratio-ok-beam ?ok))
	(test (<> (str-compare ?ok TRUE) 0))
	=>
	(assert (web-to-thickness-beam-ratio-valid ?conn-id ?beam-id FALSE))
)

; Rule commutating results of all checks. 
; If all of them returned true the beam is fine with limitations
(defrule check-beam-limitations
    (declare (salience 9996))
	(beam-shape-to-production-procedure-valid ?conn-id ?beam-id TRUE)
	(size-to-range-valid ?conn-id ?beam-id TRUE)
	(weight-per-lf-to-max-linear-weight-valid ?conn-id ?beam-id TRUE)
	(flange-thickness-to-range-valid ?conn-id ?beam-id TRUE)
	(cutlength-depth-ratio-to-min-clear-ratio-valid ?conn-id ?beam-id TRUE)
	(web-to-thickness-beam-ratio-valid ?conn-id ?beam-id TRUE)
	=>
	(assert (beam-limitations-fine ?conn-id ?beam-id TRUE))
)

; Rule gather results of all checks. 
(defrule gather-beam-limitations-result
    (declare (salience 9996))
	(beam-shape-to-production-procedure-valid ?conn-id ?beam-id ?res1)
	(size-to-range-valid ?conn-id ?beam-id ?res2)
	(weight-per-lf-to-max-linear-weight-valid ?conn-id ?beam-id ?res3)
	(flange-thickness-to-range-valid ?conn-id ?beam-id ?res4)
	(cutlength-depth-ratio-to-min-clear-ratio-valid ?conn-id ?beam-id ?res5)
	(web-to-thickness-beam-ratio-valid ?conn-id ?beam-id ?res6)
	=>
	(assert (beam-result (id ?beam-id) (conn-id ?conn-id) 
	                     (beam-shape-to-production-procedure-valid ?res1) 
						 (size-to-range-valid ?res2) 
						 (weight-per-lf-to-max-linear-weight-valid ?res3)
						 (flange-thickness-to-range-valid ?res4)
						 (cutlength-depth-ratio-to-min-clear-ratio-valid ?res5)
						 (web-to-thickness-beam-ratio-valid ?res6)
						 ))
)

;;==============================================================
;;=======Column in connection check rules from BuildLogic=======
;;==============================================================
(deftemplate column-data
    (slot id)
	(slot member-production-procedure)
	(slot rolled-shapes)
	(slot size)	
	(slot weight-per-lf)
	(slot top-flange-thickness)
	(slot depth)
)

(deftemplate column-result
	(slot id)
	(slot conn-id)
	(slot column-shape-to-production-procedure-valid)
	(slot column-size-valid)
	(slot web-to-thickness-column-ratio-valid)
)

;Checks whether column shape is supported
(defrule valid-column-shape-to-production-procedure
    (declare (salience 9997))
	(connection-data (id ?conn-id) (column-id ?column-id))
	(column-data (id ?column-id) (member-production-procedure ?mpp) (rolled-shapes ?rs) (size ?size))
	(and
		(test (= (str-compare ?mpp Rolled) 0))
		(test (= (str-compare ?rs WideFlange) 0))
	)
	=>
	(assert (column-shape-to-production-procedure-valid ?conn-id ?column-id TRUE))
)

;Checks whether column shape is not supported
(defrule not-valid-column-shape-to-production-procedure
    (declare (salience 9997))
	(connection-data (id ?conn-id) (column-id ?column-id))
	(column-data (id ?column-id) (member-production-procedure ?mpp) (rolled-shapes ?rs) (size ?size))
	(not
		(and
			(test (= (str-compare ?mpp Rolled) 0))
			(test (= (str-compare ?rs WideFlange) 0))
		)
	)
	=>
	(assert (column-shape-to-production-procedure-valid ?conn-id ?column-id FALSE))
)

;Checks whether column size is in allowed range for the connection
(defrule valid-column-size
    (declare (salience 9997))
	(connection-data (id ?conn-id) (column-id ?column-id) (max-column-depth ?maxcd))
	(column-data (id ?column-id) (size ?size))
	(test (<= ?size ?maxcd))
	=>
	(assert (column-size-valid ?conn-id ?column-id TRUE))
)

;Checks whether column size is not in allowed range for the connection
(defrule not-valid-column-size
    (declare (salience 9997))
	(connection-data (id ?conn-id) (column-id ?column-id) (max-column-depth ?maxcd))
	(column-data (id ?column-id) (size ?size))
	(test (> ?size ?maxcd))
	=>
	(assert (column-size-valid ?conn-id ?column-id FALSE))
)

;Checks whether column web to thickness ratio is ok for current connection
(defrule valid-web-to-thickness-col-ratio
    (declare (salience 9997))
	(connection-data (id ?conn-id) (column-id ?column-id) (web-to-thickness-ratio-ok-column ?ok))
	(test (= (str-compare ?ok TRUE) 0))
	=>
	(assert (web-to-thickness-column-ratio-valid ?conn-id ?column-id TRUE))
)

;Checks whether column web to thickness ratio is not ok for current connection
(defrule not-valid-web-to-thickness-col-ratio
    (declare (salience 9997))
	(connection-data (id ?conn-id) (column-id ?column-id) (web-to-thickness-ratio-ok-column ?ok))
	(test (<> (str-compare ?ok TRUE) 0))
	=>
	(assert (web-to-thickness-column-ratio-valid ?conn-id ?column-id FALSE))
)

; Rule commutating results of all checks. 
; If all of them returned true the column is fine with limitations
(defrule check-column-limitations
    (declare (salience 9996))
	(column-shape-to-production-procedure-valid ?conn-id ?column-id TRUE)
	(column-size-valid ?conn-id ?column-id TRUE)
	(web-to-thickness-column-ratio-valid ?conn-id ?column-id TRUE)
	=>
	(assert (column-limitations-fine ?conn-id ?column-id TRUE))
)

; Rule commutating results of all checks into result structure 
(defrule gather-column-limitations-result
    (declare (salience 9996))
	(column-shape-to-production-procedure-valid ?conn-id ?column-id ?shape-to-pp-val)
	(column-size-valid ?conn-id ?column-id ?size-valid)
	(web-to-thickness-column-ratio-valid ?conn-id ?column-id ?wtt-ratio)
	=>
	(assert (column-result (id ?column-id) (conn-id ?conn-id) (column-shape-to-production-procedure-valid ?shape-to-pp-val) (column-size-valid ?size-valid) (web-to-thickness-column-ratio-valid ?wtt-ratio)))
)

(deffunction BLGatherget-model-result-list ()
    (bind ?facts (find-all-facts ((?f model-result)) TRUE))
)

(deffunction get-connection-result-list ()
    (bind ?facts (find-all-facts ((?f connection-result)) TRUE))
)

(deffunction BLGatherget-column-result-list ()
    (bind ?facts (find-all-facts ((?f column-result)) TRUE))
)

(deffunction get-beam-result-list ()
    (bind ?facts (find-all-facts ((?f beam-result)) TRUE))
)

