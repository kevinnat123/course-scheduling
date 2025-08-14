console.warn("[ Global Loaded ]");

window.showLoading = function () {
  document.getElementById("loadingModal").style.display = "flex";
};

window.hideLoading = function () {
  document.getElementById("loadingModal").style.display = "none";
};

/**
 * @param {string} [icon] - The icon type (e.g., "success", "error", "warning", "info"). Leave as `undefined` to skip.
 * @param {string} [title] - The title text. Leave as `undefined` to skip.
 * @param {string} [text] - The message text. Leave as `undefined` to skip.
 * @param {number} [timer] - The duration in milliseconds before closing. Leave as `undefined` for default behavior.
 */
window.popUpTimer = async function (icon, title, text = null, timer = null) {
  await Swal.fire({
    position: "center",
    icon: icon ?? "error",
    title: title ?? "Terjadi kesalahan pada sistem.",
    text: text ?? null,
    showConfirmButton: false,
    timer: timer ?? Math.max(1000, title.length * 75), // Hitung timer berdasarkan panjang title (75ms per karakter, minimal 1000ms)
    timerProgressBar: true,
  });
};

$(document).on("click", ".btn-close-badge", function () {
  const $badge = $(this).closest("span.badge");
  const $formGroup = $badge.closest("div.form-group");
  const fieldId = $badge.closest("div").attr("id");

  $badge.remove(); // hapus badge
  if (!retrieveBadgeValues(fieldId).length) $formGroup.attr("hidden", true);
});

$(document).on("keydown", "form", function (e) {
  if (e.key === "Enter") {
    e.preventDefault();
    return false;
  }
});

function capitalizeWords(string) {
  return string.replace(/\b\w/g, (char) => char.toUpperCase());
}

// auto uppercase input
$('input:not([type="file"])').on("input", function () {
  if (!$(this).hasClass("sensitive-case"))
    $(this).val($(this).val().toUpperCase());
  else $(this).val($(this).val());
});

// NumberOnly & CurrencyFormat
document.addEventListener("input", function (event) {
  let value = event.target.value;

  if (event.target.classList.contains("numberOnly")) {
    // Hanya angka tanpa tanda minus (-)
    let sanitizedValue = value.replace(/[^0-9]/g, "");
    event.target.value = sanitizedValue;
  }

  if (event.target.classList.contains("negativeNumber")) {
    // Hanya angka dan bisa memiliki satu '-' di depan
    let sanitizedValue = value.replace(/[^0-9-]/g, "").replace(/(?!^)-/g, "");
    event.target.value = sanitizedValue;
  }

  if (event.target.classList.contains("yearInput")) {
    event.target.value = yearInput(event.target.value);
  }

  if (event.target.classList.contains("currencyFormat")) {
    // Format mata uang, boleh negatif
    let sanitizedValue = value.replace(/[^0-9-]/g, "").replace(/(?!^)-/g, "");
    event.target.value =
      sanitizedValue === "" ? "" : formatCurrency(sanitizedValue);
  }
});

/**
 * Retrieve values of checked Item.
 *
 * @param {string} [Name] - Item's name attribute
 */
function getCheckedItemValue(Name) {
  return $("input[name=" + Name + "]:checked")
    .map(function () {
      return this.value;
    })
    .get();
}

/**
 * Retrieve values of badges inside a div.
 *
 * @param {string} [div_list_id] - Div's ID
 */
function retrieveBadgeValues(div_list_id) {
  let values = [];

  $("#" + div_list_id + " span.badge").each(function () {
    let text = $(this)
      .clone()
      .children()
      .remove()
      .end()
      .text()
      .trim()
      .toUpperCase();
    if (!values.includes(text)) values.push(text);
  });

  return values;
}

function addBadge(container_id, div_list_id, value) {
  current_badge_values = retrieveBadgeValues(div_list_id);
  if (!current_badge_values.includes(value)) {
    if ($("#" + container_id).prop("hidden") === true)
      $("#" + container_id).attr("hidden", false);
    $("#" + div_list_id).append(
      `<span class="badge bg-primary me-2">` +
        value +
        `<button type="button" class="btn-close btn-close-white btn-close-badge ms-1" aria-label="Close"></button>
              </span>`
    );
  } else
    popUpTimer(
      "info",
      div_list_id.substring(5) + " '" + value + "' sudah anda input!",
      "Silahkan input " + div_list_id.substring(5) + " lain!"
    );
}

async function clearBadge(container_id, div_list_id) {
  if (retrieveBadgeValues(div_list_id).length > 0)
    await Swal.fire({
      title:
        "Yakin akan hapus semua data " +
        div_list_id.replaceAll("_", " ").substring(5) +
        "?",
      showDenyButton: true,
      confirmButtonText: "Ya",
      denyButtonText: `Batal`,
    }).then((result) => {
      if (result.isConfirmed) {
        $("#" + div_list_id + " span.badge").remove();
        $("#" + container_id).attr("hidden", true);
      } else if (result.isDenied) {
        return;
      }
    });
}

function getDatatableData(dataTable, index = undefined) {
  let tableId = dataTable.table().node().id; // ambil id table yang digunakan pada dataTable
  let tableData = dataTable.data().toArray(); // Ambil semua data dari dataTable
  let columnNames = dataTable
    .settings()
    .init()
    .columns.map((col) => col.data); // Ambil nama kolom dari DataTable

  if (index >= 0) {
    let row = $("#" + tableId + " tbody tr:eq(" + index + ")");
    let temp = tableData[index];
    tableData = [];

    if (row.length) {
      row.find("td").each(function (colIndex) {
        let inputField = $(this).find("input");
        if (inputField.length > 0 && columnNames[colIndex]) {
          temp[columnNames[colIndex]] = inputField.val();
        }

        // let value =
        //   inputField.length > 0 ? inputField.val() : $(this).text().trim();

        // if (columnNames[colIndex]) {
        //   temp[columnNames[colIndex]] = value;
        // }
      });
    }
    tableData.push(temp);
  } else {
    $("#" + tableId + " tbody tr").each(function (rowIndex) {
      $(this)
        .find("td")
        .each(function (colIndex) {
          let inputField = $(this).find("input");
          if (inputField.length > 0 && columnNames[colIndex]) {
            tableData[rowIndex][columnNames[colIndex]] = inputField.val(); // Update berdasarkan nama kolom
          }
        });
    });
  }

  return index >= 0 ? tableData[0] : tableData;
}

/**
 * Creating empty row contains of empty columns data of the specified datatable.
 */
window.createEmptyRow = function (dataTable) {
  let emptyRow = {};
  dataTable.columns().every(function (index) {
    let columnData = this.dataSrc();
    if (columnData !== null) emptyRow[columnData] = "";
  });
  return emptyRow;
};

/**
 * Adding a new row to the specified datatable.
 */
window.addRow = function (dataTable) {
  if (dataTable.rows().count() > 0) {
    // cek apakah datatable punya baris ?
    let tableId = dataTable.table().node().id; // ambil id table yang digunakan pada datatable
    let lastRow = $("#" + tableId + " tbody tr:last td:first input")
      .val()
      .trim();
    if (!lastRow) return false;
  }

  let emptyRow = createEmptyRow(dataTable);

  dataTable.row.add(emptyRow).draw(false);

  return true;
};

window.addRowButton = function (dataTable) {
  let tableId = dataTable.table().node().id; // ambil id table yang digunakan pada datatable

  addRow(dataTable);

  $("#" + tableId + " tbody tr:last td:first input")
    .click()
    .focus();

  return true;
};

window.yearInput = function (targetValue) {
  let today = new Date();
  let currentYear = today.getFullYear();
  let maxYear = today.getMonth() > 3 ? currentYear : currentYear - 1; // Agustus = index 7
  let minYear = maxYear - 7;

  // Hanya angka & maksimal 4 digit
  let sanitizedValue = targetValue.replace(/[^0-9]/g, "").slice(0, 4);

  // Jika sudah 4 digit, cek apakah dalam rentang yang diizinkan
  if (sanitizedValue.length === 4) {
    let year = parseInt(sanitizedValue, 10);
    if (year < minYear) {
      popUpTimer("error", "Angkatan " + year + " terlalu tua!");
      sanitizedValue = minYear; // Ubah ke tahun tertua jika tidak valid
    } else if (year > maxYear) {
      popUpTimer("error", "Angkatan " + year + " belum ada!");
      sanitizedValue = maxYear; // Ubah ke tahun termuda jika tidak valid
    }
  }

  return sanitizedValue;
};
