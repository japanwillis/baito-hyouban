/** Monthly pay estimates. No taxes, insurance, or labor-law assumptions. */
const WEEKS_PER_YEAR = 52;
const MONTHS_PER_YEAR = 12;
function numeric(value, name, min, max) {
  const n = typeof value === 'number' ? value : Number(value);
  if (typeof value === 'boolean' || value === '' || value === null || !Number.isFinite(n) || n < min || n > max)
    throw new RangeError(name + ' is out of range');
  return n;
}
export function calculateIncome(config) {
  if (!config || typeof config !== 'object') throw new TypeError('Invalid configuration');
  const mode = config.mode;
  if (mode !== 'weekly' && mode !== 'monthly') throw new RangeError('Invalid schedule mode');
  const hourlyYen = numeric(config.hourlyYen, 'hourlyYen', 1, 100000);
  const hours = numeric(config.hours, 'hours', 0.25, 24);
  const breakMinutes = numeric(config.breakMinutes, 'breakMinutes', 0, 1440);
  const paidHours = hours - breakMinutes / 60;
  if (paidHours <= 0) throw new RangeError('Paid hours must be positive');
  const shifts = numeric(config.shifts, 'shifts', 0.25, mode === 'weekly' ? 7 : 31);
  const farePerShift = numeric(config.farePerShift, 'farePerShift', 0, 100000);
  const costPerShift = numeric(config.costPerShift, 'costPerShift', 0, 100000);
  const monthlyDeductions = numeric(config.monthlyDeductions, 'monthlyDeductions', 0, 1000000);
  const shiftsPerMonth = mode === 'weekly' ? shifts * WEEKS_PER_YEAR / MONTHS_PER_YEAR : shifts;
  const monthlyHours = paidHours * shiftsPerMonth;
  const monthlyWages = Math.round(hourlyYen * monthlyHours);
  const monthlyFare = Math.round(farePerShift * shiftsPerMonth);
  const monthlyCosts = Math.round(costPerShift * shiftsPerMonth);
  const monthlyGrossWithFare = monthlyWages + monthlyFare;
  const estimatedRemainder = monthlyGrossWithFare - monthlyCosts - monthlyDeductions;
  return {
    paidHours,
    shiftsPerMonth,
    monthlyHours,
    monthlyWages,
    annualWages: monthlyWages * MONTHS_PER_YEAR,
    monthlyFare,
    monthlyCosts,
    monthlyDeductions,
    monthlyGrossWithFare,
    estimatedRemainder
  };
}
export const defaults = Object.freeze({
  mode: 'weekly', hourlyYen: 1200, hours: 5, breakMinutes: 0,
  shifts: 3, farePerShift: 0, costPerShift: 0, monthlyDeductions: 0
});
