// Get server address
// Checks if LOCAL_SERVER is defined in server.js, otherwise default to external server
SERVER = typeof LOCAL_SERVER === 'undefined' ? 'https://barrettj12-crud-app.herokuapp.com' : LOCAL_SERVER

// Get page elements
nameInput = document.getElementById('tablename')
pwdInput = document.getElementById('tablepwd')
tableDisplay = document.getElementById('tableDisplay')
colnameInput = document.getElementById('colname')
masterTable = document.getElementById('masterTable')



//---- API METHODS --------------------


// API test
async function runTest() {
  makeReq('/test')
}

// Make new table
async function makeTable() {
  const formData = new FormData()
  formData.append('name', nameInput.value)
  formData.append('pwd', pwdInput.value)

  makeReq('/maketable',

    // Code to run on response
    (msg) => {
      alert(msg)
      viewTable()
      getTables() 
    }, {

    // Options
    mthd: 'POST',
    body: formData
  })
}

// View table
async function viewTable() {
  makeReq('/viewtable',

    // Code to run on response
    (data) => {
      elmt = formatTable(data, true)
      tableDisplay.replaceChildren(elmt)
    }, {
      
    // Options
    qparams: { name: nameInput.value },
    isJSON: true
  })
}

// Add row to table
async function addRow() {
  makeReq('/addrow',

    // Code to run on response
    () => {
      viewTable()
    }, {
      
    // Options
    qparams: { name: nameInput.value },
    mthd: 'POST'
  })
}

async function deleteRow(rowid) {
  window.confirm('Are you sure you want to delete row ' + rowid + '?')
}

// Add column to table
async function addCol() {
  makeReq('/addcol',

    // Code to run on response
    (msg) => {
      alert(msg)
      viewTable()
    }, {
      
    // Options
    qparams: {
      name: nameInput.value,
      newcol: colnameInput.value,
      /* datatype: getColDataType() */
    },
    mthd: 'POST'
  })
}

// Delete column from table
async function deleteCol(colname) {
  window.confirm('Are you sure you want to delete column "' + colname + '"?')
}

// Update value
async function update(row,col,value) {
  console.log('Update value in row "' + row + '" and column "' + col + '" with value "' + value + '".')

  makeReq('/update',

    // Code to run on response
    (msg) => {
      alert(msg)
    }, {
      
    // Options
    qparams: {
      name: nameInput.value,
      row: row,
      col: col,
      value: value
    },
    mthd: 'PUT'
  })
}

// Sort by column
async function sortByCol(colname) {
  alert('Sorting by column "' + colname + '"')
}

// Delete table
async function deleteTable() {
  makeReq('/deletetable',

    // Code to run on response
    (msg) => {
      alert(msg)
      tableDisplay.replaceChildren()
      getTables()
      nameInput.value = ""
      pwdInput.value = ""
    }, {
      
    // Options
    qparams: {
      name: nameInput.value
    },
    mthd: 'DELETE'
  })
}



//---- ADMIN API METHODS --------------


// Get tables
async function getTables() {
  makeReq('/tables',

    // Code to run on response
    (data) => {
      elmt = formatTable(data, false)
      masterTable.replaceChildren(elmt)
    }, {
      
    // Options
    isJSON: true
  })
}

// Reset ALL data
async function reset() {
  if (window.confirm('Are you sure you want to delete all data?')) {

    makeReq('/reset',

      // Code to run on response
      (msg) => {
        alert(msg)
        tableDisplay.replaceChildren()
        getTables()
      }, {
        
      // Options
      mthd: 'DELETE'
    })
  }
}



//---- HELPER METHODS -----------------


/* Create and handle fetch requests correctly.
 * Call it like this:
 *     makeReq('/api-name')
 * or
 *     makeReq('/api-name', (data) => process(data))
 * or
 *     makeReq('/api-name', (data) => process(data), {
 *       qparams: {
 *         query: 'xyz',
 *         update: 'true'
 *       },
 *       mthd: 'POST'
 *     })
 */
async function makeReq(api, onOK = (data) => {
  alert(data)
  console.log(data)
},
  { qparams, mthd = 'GET', body, isJSON = false } = {}
){
  // Build query string
  qstring = ''
  for (key in qparams) {
    qstring += (qstring ? '&' : '?') + (key + "=" + qparams[key])
  }

  // Assemble options
  options = {
    method: mthd,
    headers: {
      'Authorization': pwdInput.value
    }
  }
  if (body) { options.body = body }

  // Make request
  try {
    const resp = await fetch(SERVER + api + qstring, options)
  
    if (resp.ok) {
      // Request successful (status code 2xx)
      data = await (isJSON ? resp.json() : resp.text())
      onOK(data)
    }
    else {
      st = response.status
      if (400 <= st && st <= 499) {
        // Client error
        errMsg = await resp.text()
        alert('Error: "' + errMsg + '"')
      }
      else if (st >= 500) {
        // Server error
        alert('A server error occurred.')
      }
    }
  }
  catch(err) {
    // network failure / sth prevented the request from completing
    alert('Whoops, an error occurred.')
    console.log(err)
  }
}

// Format received JSON table as HTML table
// Returns an HTMLTableElement
function formatTable(tableData, editable) {
  const table = document.createElement('table')
  //editable = true

  // Make headers
  headerRow = document.createElement('tr')

  for (hdText of tableData.fields) {
    colHeader = document.createElement('th')

    // Add column name
    hdNode = document.createTextNode(hdText)
    colHeader.appendChild(hdNode)

    if (editable) {
      // Add buttons
      if (hdText !== 'id') {
        rmBt = newRmBt()
        rmBt.setAttribute("onclick", "deleteCol('" + hdText + "')")
        colHeader.appendChild(rmBt)
      }

      sortBt = document.createElement('a')
      sortBt.innerHTML = '⇅'
      sortBt.setAttribute('class', 'sort-button')
      sortBt.setAttribute("onclick", "sortByCol('" + hdText + "')")
      colHeader.appendChild(sortBt)
    }

    headerRow.appendChild(colHeader)
  }

  table.appendChild(headerRow)

  // Make rows
  for (rowData of tableData.data) {
    nextRow = document.createElement('tr')

    for (i in rowData) {
      txt = rowData[i] == null ? '' : rowData[i]
      cell = document.createElement('td')

      // Create cell content
      txtNode = document.createElement('input')
      txtNode.setAttribute("type", "text")
      txtNode.setAttribute("value", txt)
      txtNode.setAttribute("onchange", "update('" + rowData[0] + "','" + tableData.fields[i] + "',this.value)")

      if (tableData.fields[i] == 'id') {
        txtNode.setAttribute("type", "text")
        txtNode.setAttribute("class", "rowid")
        txtNode.setAttribute("disabled", "")
      }
      if (!editable) {
        txtNode.setAttribute("disabled", "")
      }

      cell.appendChild(txtNode)
      nextRow.appendChild(cell)
    }

    if (editable) {
      // Add remove button
      rmBt = newRmBt()
      rmBt.setAttribute("onclick", "deleteRow('" + rowData[0] + "')")
      nextRow.appendChild(rmBt)
    }

    table.appendChild(nextRow)
  }

  return table;
}

// Makes a remove button for rows and columns
function newRmBt() {
  rmBt = document.createElement('a')
  rmBt.innerHTML = '✖'
  rmBt.setAttribute('class', 'remove-button')

  return rmBt
}

// Helper function to get column data type
/*       function getColDataType() {
  const chosen = document.querySelector('input[name="coldatatype"]:checked');
  
  return chosen ? chosen.value : 'none'
} */
