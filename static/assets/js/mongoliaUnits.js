// AJAX-aap Unit1,2,3 тай ажиллах бол энн fcuntion ийг санал болгож байна highly recommended

// 1. Select үүдээ unit1_id, unit2_id, unit3_id гэж үүсгэнэ.
// 2. unit1_id, unit2_id - гэсэн id тэй select дээрээ
                //onchange="if (this.value) unit1SelectHandler(this);"
                //onchange="if (this.value) unit2SelectHandler(this);" гэж оруулна
// 3. getAllUnitsX энэ function ийг л ашиглаж байгаа газраа дууд
// 4. unit1, unit2, unti3 анхны утгаараа selected байлгахыг хүсвэл
                // UNIT1 анхны утгаар select-д болчоод Unit2 ийн option өгөх бол unit1SelectHandler({ value: UNIT1_ID })
                // UNIT2 анхны утгаар select-д болчоод Unit3 ийн option өгөх бол unit2SelectHandler({ value: UNIT2_ID })

let allUnitsX = []
let unit2OptionsX = []
const defaultOp = document.createElement("option");

const unit1ElementZ = document.getElementById('unit1_id')
const unit2ElementZ = document.getElementById('unit2_id')
const unit3ElementZ = document.getElementById('unit3_id')

defaultOp.text = '-------------';
defaultOp.value = null;

// Бүх select цэвэрлэх
const clearAllUnitSelects = () =>
{
    unit1SelectHandler({ value: 'null' })
    unit2SelectHandler({ value: 'null' })

    unit1ElementZ.value = ''
    unit2ElementZ.value = ''
    unit3ElementZ.value = ''
}

// Бүх unit select анхны утга өгөх
const setDefaultValueUnitX = ({ unit1, unit2, unit3 }) =>
{

    unit1SelectHandler({ value: unit1 })
    unit2SelectHandler({ value: unit2 })

    $(`#unit1_id`).val(unit1).trigger('change')
    $(`#unit2_id`).val(unit2).trigger('change')
    $(`#unit3_id`).val(unit3).trigger('change')

    unit1ElementZ.value = unit1
    unit2ElementZ.value = unit2
    unit3ElementZ.value = unit3
}

// select дээрээ onchange="if (this.value) unit2SelectHandler(this);" ингэж ашиглана
const unit2SelectHandler = async (event) =>
{
    if(event.value === 'null')
    {
        unit3ElementZ.innerHTML = null
        const defaultOp = document.createElement("option");
        defaultOp.text = '-------------';
        defaultOp.value = null;
        unit3ElementZ.add(defaultOp);
        return
    }
    const units3 = unit2OptionsX.find((unit2) => unit2.id.toString() === event.value.toString()).unit3
    unit3ElementZ.innerHTML = null
    unit3ElementZ.add(defaultOp);
    units3.map(
        (unit2) =>
        {
            var option = document.createElement("option");
            option.text = unit2.name;
            option.value = unit2.id;
            unit3ElementZ.add(option);
        }
    )
}

// select дээрээ onchange="if (this.value) unit1SelectHandler(this);" ингэж ашиглана
const unit1SelectHandler = async (event) =>
{
    unit2SelectHandler({ value: 'null' })
    if(event.value === 'null')
    {
        unit2ElementZ.innerHTML = null
        const defaultOp = document.createElement("option");
        defaultOp.text = '-------------';
        defaultOp.value = null;
        unit2ElementZ.add(defaultOp);
        return
    }
    const units2 = allUnitsX.find((unit1) => unit1.id.toString() === event.value.toString()).unit2
    unit2OptionsX = units2
    unit2ElementZ.innerHTML = null
    unit2ElementZ.add(defaultOp);
    units2.map(
        (unit2) =>
        {
            var option = document.createElement("option");
            option.text = unit2.name;
            option.value = unit2.id;
            unit2ElementZ.add(option);
        }
    )
}


// Бүх Unit авах nested байдлаар
const getAllUnitsX = async () =>
{
    const { success, data } = await fetchData('/account/user-extra-info-units/', null, 'GET')
    if(success)
    {
        allUnitsX = data
        unit1ElementZ.add(defaultOp);
        data.map(
            (unit1) =>
            {
                var option = document.createElement("option");
                option.text = unit1.name;
                option.value = unit1.id;
                unit1ElementZ.add(option);
            }
        )
    }
}
